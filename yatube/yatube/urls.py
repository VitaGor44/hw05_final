from django.conf import settings
from django.conf.urls.static import static

from about.apps import AboutConfig
from posts.apps import PostsConfig
from users.apps import UsersConfig

from django.contrib import admin
from django.urls import path, include


handler404 = 'core.views.page_not_found'  # no found URL
handler500 = 'core.views.server_error'  # server error
handler403 = 'core.views.permission_denied'

urlpatterns = [
    path('about/', include('about.urls', namespace=AboutConfig.name)),
    path('auth/', include('users.urls', namespace=UsersConfig.name)),
    path('auth/', include('django.contrib.auth.urls')),
    path("admin/", admin.site.urls),
    path("", include('posts.urls', namespace=PostsConfig.name)),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
