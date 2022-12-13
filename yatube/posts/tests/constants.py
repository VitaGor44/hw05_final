import tempfile

from django.conf import settings
from django.urls import reverse


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

INDEX_URL = (reverse('posts:index'),
             'posts/index.html',
             '?page=2',
             )
