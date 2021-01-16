from django.contrib import admin
from django.urls import include, path
from django.conf.urls import handler404, handler500

handler404 = "posts.views.page_404" # noqa
handler500 = "posts.views.page_500" # noqa

urlpatterns = [
    path("", include("posts.urls")),
    path("auth/", include("users.urls")),
    path("auth/", include("django.contrib.auth.urls")),
    path("admin/", admin.site.urls),
    path('about/', include('about.urls', namespace='about')),
]
