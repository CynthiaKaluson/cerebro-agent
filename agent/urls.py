from django.urls import path
from . import views

# We define the app name for 'namespacing' - standard senior dev practice
app_name = 'agent'

urlpatterns = [
    # The diagnostic test we already verified
    path('test-ai/', views.test_gemini, name='test_gemini'),

    # Our new multimodal 'Eyes and Ears' endpoint
    path('process-file/', views.process_multimodal_input, name='process_file'),
]