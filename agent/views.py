from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt  # New import for security bypass
from .models import ResearchMaterial
from google import genai


def test_gemini(_request):
    """
    Diagnostic view to confirm Cerebro's heart is beating.
    """
    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents="Cerebro, confirm you are awake."
        )
        return JsonResponse({"status": "Cerebro is Alive", "message": response.text})
    except Exception as e:
        return JsonResponse({"status": "Connection Failed", "reason": str(e)}, status=500)


@csrf_exempt  # This stops the 403 Forbidden error for our API tests
def process_multimodal_input(request):
    """
    Cerebro's 'Eyes and Ears'.
    Processes uploaded research files using Gemini 3's native multimodal power.
    """
    # We check for POST and files here
    if request.method == 'POST' and request.FILES.get('research_file'):
        uploaded_file = request.FILES['research_file']

        # Save to our local archive so the AI has something to read from
        material = ResearchMaterial.objects.create(
            title=request.POST.get('title', 'New Research Upload'),
            file=uploaded_file,
            file_type=request.POST.get('file_type', 'image')
        )

        try:
            # Wake up the Brain
            client = genai.Client(api_key=settings.GEMINI_API_KEY)

            # Read the file bytes directly
            with open(material.file.path, 'rb') as doc_file:
                file_data = doc_file.read()

            # The actual 'Multimodal' magic happens here
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=[
                    "Analyze this research material. What are the core findings?",
                    file_data
                ]
            )

            # Store the wisdom
            material.analysis_result = response.text
            material.save()

            return JsonResponse({
                "status": "Success",
                "cerebro_insight": response.text,
                "record_id": material.pk
            })

        except Exception as e:
            return JsonResponse({"status": "Neural Link Error", "error": str(e)}, status=500)

    # If they send a GET or no file, we catch it here
    return JsonResponse({"status": "Failed", "message": "Send a file via POST."}, status=400)