import magic
from django.db import models as db_models
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import ResearchMaterial
from google import genai
from google.genai import types


# --- 1. THE TOOL (For Agentic Search) ---
def search_local_records(query: str):
    results = ResearchMaterial.objects.filter(
        db_models.Q(title__icontains=query) | db_models.Q(analysis_result__icontains=query)
    )
    return [{"title": r.title, "insight": r.analysis_result[:200] if r.analysis_result else "No analysis."} for r in
            results]


# --- 2. MULTIMODAL INGESTION ---
@csrf_exempt
def process_multimodal_input(request):
    if request.method != 'POST': return JsonResponse({"error": "POST only"}, status=405)
    uploaded_file = request.FILES.get('research_file')
    if not uploaded_file: return JsonResponse({"error": "No file detected"}, status=400)

    file_data = uploaded_file.read()
    mime_type = magic.from_buffer(file_data, mime=True)
    uploaded_file.seek(0)

    material = ResearchMaterial.objects.create(
        title=request.POST.get('title', uploaded_file.name),
        file=uploaded_file,
        file_type=mime_type.split('/')[0]
    )

    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_bytes(data=file_data, mime_type=mime_type),
                        types.Part.from_text(text="Analyze this as Cerebro Agent.")
                    ]
                )
            ]
        )
        material.analysis_result = response.text
        material.save()
        return JsonResponse({"status": "Success", "insight": response.text, "id": material.pk})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# --- 3. THE AGENT CHAT ---
@csrf_exempt
def agent_chat(request):
    user_query = request.GET.get('ask', '')
    if not user_query: return JsonResponse({"error": "Ask a question."}, status=400)

    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        search_tool = types.Tool(
            function_declarations=[
                types.FunctionDeclaration(
                    name="search_local_records",
                    description="Search the local database.",
                    parameters=types.Schema(
                        type=types.Type.OBJECT,
                        properties={"query": types.Schema(type=types.Type.STRING)},
                        required=["query"]
                    )
                )
            ]
        )

        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=user_query,
            config=types.GenerateContentConfig(
                tools=[search_tool],
                thinking_config=types.ThinkingConfig(include_thoughts=True, thinking_level=types.ThinkingLevel.HIGH)
            )
        )

        parts = response.candidates[0].content.parts
        function_call = next((p.function_call for p in parts if p.function_call), None)

        if function_call:
            search_data = search_local_records(function_call.args["query"])
            final_response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=[
                    types.Content(role="user", parts=[types.Part.from_text(text=user_query)]),
                    response.candidates[0].content,
                    types.Content(
                        role="tool",
                        parts=[types.Part.from_function_response(name=function_call.name,
                                                                 response={"result": search_data})]
                    )
                ]
            )
            return JsonResponse({"cerebro_answer": final_response.text})

        return JsonResponse({"cerebro_answer": response.text})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# --- 4. MANUAL SEARCH (Required by your urls.py) ---
@csrf_exempt
def search_research(request):
    query = request.GET.get('q', '')
    results = ResearchMaterial.objects.filter(
        db_models.Q(title__icontains=query) | db_models.Q(analysis_result__icontains=query))
    data = [{"title": r.title, "uploaded_at": r.uploaded_at} for r in results]
    return JsonResponse({"status": "Success", "results": data})


# --- 5. SYNTHESIZE KNOWLEDGE (The one that was missing!) ---
@csrf_exempt
def synthesize_knowledge(request):
    topic = request.GET.get('topic', '')
    materials = ResearchMaterial.objects.filter(db_models.Q(title__icontains=topic))
    if not materials.exists(): return JsonResponse({"error": "No data found"}, status=404)

    context = "\n".join([f"Source: {m.title}\nInsight: {m.analysis_result}" for m in materials])
    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=f"Synthesize these research materials into one report about {topic}:\n\n{context}"
        )
        return JsonResponse({"synthesis": response.text})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)