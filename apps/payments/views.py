from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.conf import settings
import stripe
from .models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeWebhookView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # Handle the event idempotently
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            payment_ref = session.get('id')
            
            payment = Payment.objects.filter(gateway_ref=payment_ref).first()
            if payment and payment.status == 'pending':
                payment.status = 'completed'
                payment.save(update_fields=['status'])
                # Grant leads or promotion based on metadata...
                
        return Response({'success': True}, status=status.HTTP_200_OK)
