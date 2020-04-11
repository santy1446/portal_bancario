
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from portal import views

urlpatterns = [
    path('', views.home, name=""),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('users/', include(('users.urls','users'), namespace='users')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)