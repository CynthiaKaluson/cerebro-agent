from django.urls import path
from . import views

app_name = 'agent'

urlpatterns = [
    path('process-file/', views.process_multimodal_input, name='process_file'),
    path('chat/', views.agent_chat, name='agent_chat'), # THE AGENT ENDPOINT
    # Keep your other URLs
    path('search/', views.search_research, name='search_research'),
    path('synthesize/', views.synthesize_knowledge, name='synthesize_knowledge'),
]