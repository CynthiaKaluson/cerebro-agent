import magic
from django.db import models as db_models
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import ResearchMaterial
from google import genai
from google.genai import types


# --- 1. THE TOOL ---
def search_local_records(query: str):
    """Searches the internal database. This is the 'tool' Gemini will use."""
    results = ResearchMaterial.objects.filter(
        db_models.Q(title__icontains=query) | db_models.Q(analysis_result__icontains=query)
    )
    return [{"title": r.title, "insight": r.analysis_result[:200] if r.analysis_result else "N/A"} for r in results]


# --- 2. MULTIMODAL INGESTION ---
@csrf_exempt
def process_multimodal_input(request):
    if request.method != 'POST': return JsonResponse({"error": "Use POST"}, status=405)

    uploaded_file = request.FILES.get('research_file')
    if not uploaded_file: return JsonResponse({"error": "No file"}, status=400)

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
            model="gemini-2.0-flash-exp",
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_bytes(data=file_data, mime_type=mime_type),
                        types.Part.from_text(text="Act as Cerebro. Analyze this file deeply.")
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

        # Fixed Schema to remove PyCharm warning
        search_tool = types.Tool(
            function_declarations=[
                types.FunctionDeclaration(
                    name="search_local_records",
                    description="Search through the local database for research notes and files.",
                    parameters=types.Schema(
                        type="OBJECT",
                        properties={
                            "query": types.Schema(type="STRING", description="The search keyword")
                        },
                        required=["query"]
                    )
                )
            ]
        )

        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=user_query,
            config=types.GenerateContentConfig(tools=[search_tool])
        )

        first_part = response.candidates[0].content.parts[0]
        if first_part.function_call:
            call = first_part.function_call
            if call.name == "search_local_records":
                search_data = search_local_records(call.args["query"])
                final_response = client.models.generate_content(
                    model="gemini-2.0-flash-exp",
                    contents=f"Context from DB: {search_data}. Question: {user_query}. Answer helpfully."
                )
                return JsonResponse({"cerebro_answer": final_response.text, "tool_used": "Database_Search"})

        return JsonResponse({"cerebro_answer": response.text})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# --- 4. MANUAL SEARCH & SYNTHESIS ---
@csrf_exempt
def search_research(request):
    query = request.GET.get('q', '')
    results = ResearchMaterial.objects.filter(
        db_models.Q(title__icontains=query) | db_models.Q(analysis_result__icontains=query)
    )
    data = [{"title": r.title, "uploaded_at": r.uploaded_at} for r in results]
    return JsonResponse({"status": "Success", "results": data})


@csrf_exempt
def synthesize_knowledge(request):
    topic = request.GET.get('topic', '')
    materials = ResearchMaterial.objects.filter(db_models.Q(title__icontains=topic))
    if not materials.exists(): return JsonResponse({"error": "No data"}, status=404)
    context = "\n".join([f"{m.title}: {m.analysis_result}" for m in materials])
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    response = client.models.generate_content(model="gemini-2.0-flash-exp", contents=f"Synthesize: {context}")
    return JsonResponse({"synthesis": response.text})