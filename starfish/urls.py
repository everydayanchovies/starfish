from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.urls import re_path, path, url
from django.views.i18n import JavaScriptCatalog
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from ckeditor_uploader import views as ckeditor_views

admin.autodiscover()

urlpatterns = [
    # Uncomment the admin/doc line below to enable admin documentation:
    re_path(r"^admin/doc/", include("django.contrib.admindocs.urls")),
    # Uncomment the next line to enable the admin:
    re_path(r"^admin/", admin.site.urls),
    re_path(r"", include("search.urls")),
    re_path(r"^dashboard/", include("dashboard.urls")),
    url(r"^ckeditor/upload/", login_required(ckeditor_views.upload), name="ckeditor_upload"),
    url(r"^ckeditor/browse/", never_cache(login_required(ckeditor_views.browse)), name="ckeditor_browse"),
    path("jsi18n/", JavaScriptCatalog.as_view(), name="jsi18n"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns.append(path("__debug__/", include("debug_toolbar.urls")))
