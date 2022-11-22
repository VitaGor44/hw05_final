from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'posts'

urlpatterns = [
    path("", views.index, name="index"),
    path("follow/", views.follow_index, name="follow_index"),
    path("profile/<str:username>/follow/", views.profile_follow,
         name="profile_follow"),
    path("profile/<str:username>/unfollow/", views.profile_unfollow,
         name="profile_unfollow"),
    path("group/<slug:slug>/", views.group_posts, name="group_list"),
    # Профайл пользователя
    path("profile/<str:username>/", views.profile, name="profile"),
    # Просмотр записи
    path("posts/<int:post_id>/", views.post_detail, name="post_detail"),
    path("create/", views.post_create, name="post_create"),
    path("posts/<int:post_id>/edit/", views.post_edit, name="post_edit"),
    path('posts/<int:post_id>/comment/',
         views.add_comment, name='add_comment'),
    path("404/", views.page_not_found, name="404"),
    path("500/", views.server_error, name="500"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
