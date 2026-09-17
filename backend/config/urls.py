from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve
import os

def serve_frontend(request, path=''):
    if not path or path == '/':
        path = 'index.html'
    frontend_dir = settings.BASE_DIR.parent / 'frontend'
    file_path = frontend_dir / path
    if not os.path.exists(file_path):
        # Fallback to index.html if file doesn't exist
        path = 'index.html'
    return serve(request, path, document_root=frontend_dir)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # REST API Routes
    path('api/auth/', include('users.urls')),
    path('api/containers/', include('containers.urls')),
    path('api/sensors/', include('sensors.urls')),
    path('api/vision/', include('vision.urls')),
    path('api/risk/', include('risk.urls')),
    path('api/actions/', include('actions.urls')),
    path('api/alerts/', include('alerts.urls')),
    path('api/collection/', include('collection.urls')),
    path('api/analytics/', include('analytics.urls')),
    path('api/audit-logs/', include('audit_logs.urls')),
    path('api/devices/', include('devices.urls')),
    
    # Serve all Frontend pages & assets directly via Django
    re_path(r'^(?P<path>.*)$', serve_frontend),
]
