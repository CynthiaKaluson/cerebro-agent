from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import ResearchMaterial
from google import genai
from google.genai import types

# TONE & BEHAVIOR: Ensures Cerebro acts as a peer and avoids robotic Markdown
SYSTEM_INSTRUCTION = (
    "You are Cerebro, an adaptive Research Agent. "
    "1. TONE: Observe the user's emotion and tone; be a helpful peer. "
    "2. FORMATTING: Never use # or * symbols. Use plain text with clear spacing. "
    "3. LANGUAGES: Respond in the language requested or detected. "
    "4. CAPABILITY: You analyze multimodal data. Provide narrative summaries."
)


def index(request):
    materials = ResearchMaterial.objects.all().order_by('-uploaded_at')
    return render(request, 'agent/index.html', {'materials': materials})


@csrf_exempt
def process_multimodal_input(request):
    """Processes uploads and triggers immediate AI analysis."""
    if request.method != "POST":
        return JsonResponse({"status": "Error", "error": "Invalid method"}, status=405)

    uploaded_file = request.FILES.get('research_file')
    title = request.POST.get('title', 'Untitled Research')

    if not uploaded_file:
        return JsonResponse({"status": "Error", "error": "No file provided"}, status=400)

    material = ResearchMaterial.objects.create(
        title=title, file=uploaded_file, file_type='multimodal'
    )

    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    try:
        with open(material.file.path, 'rb') as f:
            file_data = f.read()

        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[
                types.Part.from_bytes(data=file_data, mime_type=uploaded_file.content_type),
                f"Analyze '{title}'. Provide a deep narrative summary and key takeaways."
            ],
            config=types.GenerateContentConfig(temperature=0.7)
        )

        clean_analysis = response.text.replace('#', '').replace('*', '')
        material.analysis_result = clean_analysis
        material.save()

        return JsonResponse({"status": "Success", "analysis": clean_analysis})
    except Exception as e:
        return JsonResponse({"status": "Error", "error": str(e)}, status=500)


def agent_chat(request):
    """Handles persistent conversation and session-based memory."""
    user_query = request.GET.get('ask', '')
    new_chat = request.GET.get('new_chat') == 'true'

    if 'history' not in request.session or new_chat:
        request.session['history'] = []
        if new_chat:
            return JsonResponse({"status": "cleared"})

    if not user_query:
        return JsonResponse({"error": "No query provided"}, status=400)

    history = request.session['history']
    latest_research = ResearchMaterial.objects.exclude(analysis_result__isnull=True).last()

    vault_context = ""
    if latest_research:
        vault_context = f"Context from Research Vault ({latest_research.title}): {latest_research.analysis_result}"

    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    try:
        prompt_parts = [SYSTEM_INSTRUCTION, vault_context] + history + [user_query]

        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt_parts,
            config=types.GenerateContentConfig(temperature=0.8)
        )

        answer = response.text.replace('#', '').replace('*', '')
        history.append(f"User: {user_query}")
        history.append(f"Cerebro: {answer}")
        request.session['history'] = history[-10:]
        request.session.modified = True

        return JsonResponse({
            "cerebro_answer": answer,
            "agent_logic": "Contextual reasoning complete."
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def export_document(request):
    """Exports the last intelligence response to a TXT file."""
    history = request.session.get('history', [])
    if not history:
        return HttpResponse("No content to export", status=400)

    content = history[-1]
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="cerebro_export.txt"'
    return response