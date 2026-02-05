from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import ResearchMaterial
from google import genai
from google.genai import types


def index(request):
    materials = ResearchMaterial.objects.all().order_by('-uploaded_at')
    return render(request, 'agent/index.html', {'materials': materials})


@csrf_exempt  # This fixes the 'Forbidden (CSRF token missing)' error
def process_multimodal_input(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get('research_file')
        title = request.POST.get('title', 'Untitled Research')

        if not uploaded_file:
            return JsonResponse({"status": "Error", "error": "No file provided"}, status=400)

        material = ResearchMaterial.objects.create(
            title=title, file=uploaded_file, file_type='video'
        )

        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_level=types.ThinkingLevel.LOW),
            media_resolution=types.MediaResolution.MEDIA_RESOLUTION_LOW,
            temperature=1.0
        )

        try:
            # Important: Use the file path for video processing
            with open(material.file.path, 'rb') as doc_file:
                file_data = doc_file.read()

            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=[
                    types.Part.from_bytes(data=file_data, mime_type=uploaded_file.content_type),
                    f"Analyze this research material titled '{title}'. Summarize key points."
                ],
                config=config
            )
            material.analysis_result = response.text
            material.save()
            return JsonResponse({"status": "Success", "analysis": response.text})
        except Exception as e:
            return JsonResponse({"status": "Error", "error": str(e)}, status=500)

    return JsonResponse({"status": "Error", "error": "Invalid method"}, status=400)


def agent_chat(request):
    user_query = request.GET.get('ask', '').lower()
    if not user_query:
        return JsonResponse({"error": "No query"}, status=400)

    # FEATURE: Fetch the latest analyzed research to provide context
    latest_research = ResearchMaterial.objects.exclude(analysis_result__isnull=True).last()
    context = ""
    if latest_research and "video" in user_query or "content" in user_query:
        context = f"The user recently uploaded a file titled '{latest_research.title}'. Its analysis is: {latest_research.analysis_result}. "

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    try:
        # We combine the context from the DB with the user's question
        full_prompt = f"{context} User Question: {user_query}"

        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=full_prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_level=types.ThinkingLevel.LOW)
            )
        )

        return JsonResponse({
            "cerebro_answer": response.text,
            "agent_logic": "Context retrieved from Research Vault. Synthesizing..."
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)