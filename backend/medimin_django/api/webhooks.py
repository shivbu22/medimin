from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings

@method_decorator(csrf_exempt, name='dispatch')
class N8NCallbackView(APIView):
    """
    Endpoint for n8n to call back after processing a medicine crawl.
    """
    def post(self, request):
        # 1. Verify Secret Key
        received_secret = request.headers.get('X-Webhook-Secret')
        if not received_secret or received_secret != settings.MEDIMIN_WEBHOOK_SECRET:
            print("[n8n Callback] Unauthorized access attempt.")
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        # 2. Extract Data
        query = request.data.get('query')
        status_msg = request.data.get('status', 'finished')
        
        if not query:
            return Response({"error": "Missing query"}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Reset syncing flag
        from .models import Medicine
        try:
            # Try to match by name or slug
            med = Medicine.objects.filter(name__iexact=query).first() or Medicine.objects.filter(slug__iexact=query).first()
            if med:
                med.is_syncing = False
                med.save()
                print(f"[n8n Callback] Reset is_syncing for {med.name}")
        except Exception as e:
            print(f"Error resetting syncing flag for '{query}': {e}")

        print(f"[n8n Callback] Crawl for '{query}' finished with status: {status_msg}")
        
        return Response({
            "message": "Callback received",
            "query": query,
            "status": status_msg
        }, status=status.HTTP_200_OK)
