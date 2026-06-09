from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.conf import settings
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from drf_spectacular.utils import extend_schema
import logging

from .models import Payment
from core.utils import send_response

logger = logging.getLogger(__name__)

# Lazy init — don't crash at import if stripe isn't configured
try:
    import stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY
except Exception:
    stripe = None
    logger.warning("Stripe SDK not configured.")


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    """
    Receives Stripe webhook events. Verifies signature for security.
    Handles events idempotently — a completed payment won't be processed twice.
    """
    permission_classes = [permissions.AllowAny]
    authentication_classes = []  # Stripe webhooks don't carry JWT
    throttle_classes = []  # Don't throttle webhook calls from Stripe

    @extend_schema(exclude=True)
    def post(self, request):
        if not stripe:
            logger.error("Stripe webhook received but stripe SDK is not configured.")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            logger.warning("Stripe webhook: invalid payload")
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError:
            logger.warning("Stripe webhook: signature verification failed")
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # Handle the event idempotently
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            payment_ref = session.get('id')

            payment = Payment.objects.filter(gateway_ref=payment_ref).first()
            if payment and payment.status == 'pending':
                payment.status = 'completed'
                payment.completed_at = timezone.now()
                payment.save(update_fields=['status', 'completed_at'])
                logger.info("Payment %s marked completed via Stripe webhook.", payment.id)

        return Response({'success': True}, status=status.HTTP_200_OK)
