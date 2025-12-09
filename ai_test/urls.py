from django.contrib import admin
from django.urls import path, include  # 'include' import karna zaroori hai
from django.conf import settings             # <-- Import this
from django.conf.urls.static import static
urlpatterns = [
    path("admin/", admin.site.urls),
    # Root URL (/) par request 'app' ke urls.py mein bhej do
    path("", include("app.urls")),
    path('test/', include('user_tests.urls')), 
path('recruitment/', include('recruitment.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)