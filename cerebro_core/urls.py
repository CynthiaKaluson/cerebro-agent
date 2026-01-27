from django.contrib import admin
from django.urls import path, include  # Make sure 'include' is imported
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # This 'includes' all the URLs we just defined in agent/urls.py
    path('', include('agent.urls')),
]

# Ensure media files are accessible during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)