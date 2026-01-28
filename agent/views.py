import magic
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import ResearchMaterial
from google import genai


@csrf_exempt
def test_gemini(_request):
    """
    Standard heartbeat check to verify the neural link with Gemini 3.
    Required for baseline system diagnostics.
    """
    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents="Cerebro: System check. Are you operational?"
        )
        return JsonResponse({"status": "Online", "message": response.text})
    except Exception as e:
        return JsonResponse({"status": "Offline", "error": str(e)}, status=500)


@csrf_exempt
def process_multimodal_input(request):
    """
    Cerebro's Multimodal Engine.
    Handles high-speed ingestion of Images, Audio, and Video.
    Leverages Gemini 3 Flash for near-instant contextual analysis.
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed. Use POST."}, status=405)

    uploaded_file = request.FILES.get('research_file')
    if not uploaded_file:
        return JsonResponse({"error": "No file detected in request."}, status=400)

    # 1. Professional Metadata Extraction
    # We use python-magic to detect the real file type, making the API 'smart'
    file_buffer = uploaded_file.read(2048)
    mime_type = magic.from_buffer(file_buffer, mime=True)
    uploaded_file.seek(0)  # Reset pointer after reading

    # 2. Database Persistence
    # Saving the record first ensures we don't lose track of the user's data
    material = ResearchMaterial.objects.create(
        title=request.POST.get('title', f"Upload {uploaded_file.name}"),
        file=uploaded_file,
        file_type=mime_type.split('/')[0]  # Stores 'image', 'video', etc.
    )

    try:
        # 3. Initialize Gemini 3 Client
        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        # 4. Multimodal Processing
        # We send the raw bytes for speed. For large videos (>20MB),
        # we will later implement the File API upload method.
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[
                "Act as Cerebro, an AI Knowledge Agent. Analyze this material. "
                "Provide a summary, extract key data points, and suggest next steps.",
                uploaded_file.read()
            ]
        )

        # 5. Wisdom Archiving
        material.analysis_result = response.text
        material.save()

        return JsonResponse({
            "status": "Success",
            "agent_response": {
                "insight": response.text,
                "file_type_detected": mime_type,
                "record_id": material.pk
            }
        })

    except Exception as e:
        return JsonResponse({
            "status": "Neural Link Error",
            "trace": str(e)
        }, status=500)