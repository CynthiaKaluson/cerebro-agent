from django.urls import path
from . import views

app_name = 'agent' 

urlpatterns = [
    path('test-gemini/', views.test_gemini, name='test_gemini'),
    path('process-file/', views.process_multimodal_input, name='process_file'),
    path('search/', views.search_research, name='search_research'),
]