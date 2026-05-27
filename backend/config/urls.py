from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path, include
from .utils import get_hashed_url

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    # path(get_hashed_url('ht'), include('health_check.urls')),
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
