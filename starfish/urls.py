from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.urls import re_path, path
from django.views.i18n import JavaScriptCatalog

admin.autodiscover()

urlpatterns = [
    # Uncomment the admin/doc line below to enable admin documentation:
    re_path(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    re_path(r'^admin/', admin.site.urls),
    re_path(r'', include('search.urls')),
    re_path(r'^dashboard/', include('dashboard.urls')),
    re_path(r'^ckeditor/', include('ckeditor_uploader.urls')),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='jsi18n'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns.append(path('__debug__/', include('debug_toolbar.urls')))
