from django.http import JsonResponse
from google import genai
from django.conf import settings


def test_gemini(request):
    """
    Diagnostic view to confirm Cerebro is correctly
    authenticated with Google's infrastructure.
    """
    try:
        # Initialize the Client
        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        # FIX: Using 'gemini-1.5-flash-002' which is the specific stable version
        # Or you can try 'gemini-2.0-flash' to use the Hackathon's preferred model
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents="Cerebro reporting for duty. Confirm connection."
        )

        return JsonResponse({
            "status": "Cerebro is Alive",
            "message": response.text
        })

    except Exception as error:
        # Catching and returning the error so we can debug in the browser
        return JsonResponse({
            "status": "Connection Failed",
            "reason": str(error)
        }, status=500)