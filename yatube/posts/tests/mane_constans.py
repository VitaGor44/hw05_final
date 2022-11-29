import tempfile

from django.conf import settings
from django.urls import reverse

MODEL_INFO = (
    (
        'text',
        'текст',
        'Введите текст',
    ),
    (
        'pub_date',
        'дата и время публикации',
        '',
    ),
    (
        'author',
        'автор',
        '',
    ),
    (
        'group',
        'группа',
        'Выберете группу',
    ),
    (
        'image',
        'картинка',
        'Добавьте картинку',
    ),
)

PK = 1

TEST_USERNAME = 'test_user'

TEST_SLUG = 'test_slug'

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

POST_TEXT = 'Текст тестового поста'

POST_TEXT_EDITED = 'Текст тестового поста отредактирован'

INDEX_URL = (
    reverse('posts:index'),
    'posts/index.html',
    '?page=2',
)

CREATE_POST_URL = (
    reverse(
        'posts:post_create',
    ),
    'posts/create_post.html',
    None,
)

POST_EDIT_URL = (
    reverse(
        'posts:post_edit',
        args=(PK,),
    ),
    'posts/create_post.html',
    None,
)

POST_DETAIL_URL = (
    reverse(
        'posts:post_detail',
        args=(PK,),
    ),
    'posts/post_detail.html',
    None,
)

GROUP_URL = (
    reverse(
        'posts:group_list',
        args=(TEST_SLUG,),
    ),
    'posts/group_list.html',
    '?page=2',
)

PROFILE_URL = (
    reverse(
        'posts:profile',
        args=(TEST_USERNAME,),
    ),
    'posts/profile.html',
    '?page=2',
)

FOLLOW_URL = (
    reverse(
        'posts:profile_follow',
        args=(TEST_USERNAME,),
    ),
    None,
    None,
)

UNFOLLOW_URL = (
    reverse(
        'posts:profile_unfollow',
        args=(TEST_USERNAME,),
    ),
    None,
    None,
)

POST_EDIT_URLS = (POST_EDIT_URL, CREATE_POST_URL, POST_DETAIL_URL)

PAGINATED = (
    INDEX_URL,
    GROUP_URL,
    PROFILE_URL,
)

POST_CREATE_EDIT = (POST_EDIT_URL, CREATE_POST_URL)

URLS_LIST = (
    INDEX_URL,
    POST_DETAIL_URL,
    GROUP_URL,
    PROFILE_URL,
    POST_EDIT_URL,
    CREATE_POST_URL,
)


PUBLIC_URLS = (
    ('/', 'posts/index.html'),
    (
        f'/group/{TEST_SLUG}/',
        'posts/group_list.html',
    ),
    (
        f'/posts/{PK}/',
        'posts/post_detail.html',
    ),
    (
        f'/profile/{TEST_USERNAME}/',
        'posts/profile.html',
    ),
)

PRIVATE_URLS = (
    ('/create/', 'posts/create_post.html'),
    (
        f'/posts/{PK}/edit/',
        'posts/create_post.html',
    ),
)
