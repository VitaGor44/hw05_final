from django.contrib.auth import get_user_model
from django.test import TestCase
from ..models import Group, Post

User = get_user_model()

SYMBOL_PAGES = 15


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Эта текстовая запись для создания нового поста',
        )

    def test_object_name_is_title_fild(self):
        post = PostModelTest.post
        expected_object_name = post.text[:SYMBOL_PAGES]
        self.assertEqual(expected_object_name, str(post)[:SYMBOL_PAGES])
