from django.contrib import admin
from django.urls import path
from agent.views import test_gemini

urlpatterns = [
    path('admin/', admin.site.urls),
    path('test-ai/', test_gemini),
]