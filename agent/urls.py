from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('process-file/', views.process_multimodal_input, name='process_file'),
    path('chat/', views.agent_chat, name='agent_chat'),
    path('export/', views.export_document, name='export_document'),
]