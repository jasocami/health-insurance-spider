"""healthy_scrapy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/settings/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('home/', include('home.urls'))
"""
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path, include
from .utils import get_hashed_url

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    path(get_hashed_url('ht'), include('health_check.urls')),
]

# ===========================================
# Debug URLs
# ===========================================
if settings.DEBUG:
    # Server statics
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Server uploaded media
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # DEBUG TOOLBAR CONFIG
    if settings.DEBUG_TOOLBAR_ENABLED:
        import debug_toolbar
        urlpatterns = [path('__debug__/', include(debug_toolbar.urls)), ] + urlpatterns


admin.autodiscover()
admin.site.enable_nav_sidebar = False
