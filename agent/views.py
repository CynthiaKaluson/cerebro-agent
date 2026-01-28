import magic
from django.db import models as db_models
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import ResearchMaterial
from google import genai

@csrf_exempt
def test_gemini(_request):
    """Diagnostic check for Gemini 3 connectivity."""
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
    """Processes uploads and generates AI insights."""
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed. Use POST."}, status=405)

    uploaded_file = request.FILES.get('research_file')
    if not uploaded_file:
        return JsonResponse({"error": "No file detected."}, status=400)

    # Detect file type
    file_buffer = uploaded_file.read(2048)
    mime_type = magic.from_buffer(file_buffer, mime=True)
    uploaded_file.seek(0)

    # Create the record
    material = ResearchMaterial.objects.create(
        title=request.POST.get('title', f"Upload {uploaded_file.name}"),
        file=uploaded_file,
        file_type=mime_type.split('/')[0]
    )

    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[
                "Act as Cerebro, an AI Knowledge Agent. Analyze this material. Provide a concise summary and key insights.",
                uploaded_file.read()
            ]
        )
        material.analysis_result = response.text
        material.save()

        return JsonResponse({
            "status": "Success",
            "agent_response": {
                "insight": response.text,
                "record_id": material.pk,
                "timestamp": material.uploaded_at.strftime("%Y-%m-%d %H:%M")
            }
        })
    except Exception as e:
        return JsonResponse({"status": "Neural Link Error", "trace": str(e)}, status=500)

@csrf_exempt
def search_research(request):
    """Search through stored analysis results."""
    query = request.GET.get('q', '')

    if not query:
        return JsonResponse({"status": "Failed", "message": "No query provided."}, status=400)

    # Search title and AI analysis
    results = ResearchMaterial.objects.filter(
        db_models.Q(title__icontains=query) | db_models.Q(analysis_result__icontains=query)
    )

    data = []
    for item in results:
        data.append({
            "id": item.pk,
            "title": item.title,
            "file_type": item.file_type,
            "insight_snippet": item.analysis_result[:200] if item.analysis_result else "No analysis available.",
            "uploaded_at": item.uploaded_at.strftime("%Y-%m-%d %H:%M")
        })

    return JsonResponse({
        "status": "Success",
        "query": query,
        "count": len(data),
        "results": data
    })