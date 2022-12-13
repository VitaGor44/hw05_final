import shutil
import tempfile

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from mixer.backend.django import mixer

from posts.tests import constants
from ..models import Group, Post, Follow


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    INDEX_URL = (reverse('posts:index'),
                 'posts/index.html',
                 '?page=2',)
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )

        cls.user = User.objects.create(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='test-slug'
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
            group=cls.group,
            image=uploaded)

    def setUp(self):
        self.guest_client = Client()
        # Создаем авторизованный клиент
        # self.user = User.objects.create_user(username='VitaGor')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        shutil.rmtree(
            tempfile.mkdtemp(dir=settings.BASE_DIR),
            ignore_errors=True,
        )

    def test_pages_users_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={
                'slug': self.group.slug
            }): 'posts/group_list.html',
            reverse('posts:post_detail', kwargs={
                'post_id': f'{self.post.id}'
            }): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }

        # Проверяем, что при обращении к name
        # вызывается соответствующий HTML-шаблон
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Проверяем, что словарь context страницы /task
    # в первом элементе списка object_list содержит ожидаемые значения

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        # post_author_0 = first_object.author.username
        # post_group_0 = first_object.group.title
        # post_image_0 = Post.objects.first()
        # self.assertEqual(post_text_0,
        #                  'Тестовая запись для создания 1 поста')
        # self.assertEqual(post_author_0, 'test_name1')
        # self.assertEqual(post_group_0, 'Заголовок для 1 тестовой группы')
        # self.assertEqual(post_image_0, 'posts/small.gif')
        post_author_0 = first_object.author.username
        post_group_0 = first_object.group.title
        self.assertEqual(post_text_0,
                         'Тестовая группа')
        self.assertEqual(post_author_0, self.user.username)
        self.assertEqual(post_group_0, self.group.title)

    def test_group_pages_show_correct_context(self):
        """Шаблон группы"""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={
                'slug': self.group.slug
            })
        )
        first_object = response.context["group"]
        group_title_0 = first_object.title
        group_slug_0 = first_object.slug
        post_image_0 = Post.objects.first().image
        self.assertEqual(post_image_0, 'posts/small.gif')
        self.assertEqual(group_title_0, 'Тестовая группа')
        self.assertEqual(group_slug_0, 'test-slug')

    def test_post_another_group(self):
        """Пост не попал в другую группу"""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        self.assertTrue(post_text_0, 'Тестовая запись для создания 2 поста')

    def test_new_post_show_correct_context(self):
        """Шаблон сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_profile_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={
                'username': self.user.username
            })
        )
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_image_0 = Post.objects.first().image
        self.assertEqual(post_image_0, 'posts/small.gif')
        self.assertEqual(response.context['author'], self.user)
        self.assertEqual(post_text_0, self.post.text)

    def test_separate_post_correct_context(self):
        self.authorized_client.get(reverse('posts:post_detail', kwargs={
            'post_id': Post.objects.first().id}))

    def test_cache_index(self):
        """
        Список записей страницы index хранится в кеше и обновлялся
        раз в 20 секунд.
        """

        post = mixer.blend(Post)
        content = self.authorized_client.get(constants.INDEX_URL[0]).content
        post.delete
        content_after_delete = self.authorized_client.get(constants.INDEX_URL[0]).content
        self.assertEqual(content, content_after_delete)
        cache.clear()
        content_after_cacheclear = self.authorized_client.get(
            constants.INDEX_URL[0],
        ).content
        self.assertNotEqual(content, content_after_cacheclear)

    # def test_cache_index(self):
    # """
    # ЭТО ЗДЕСЬ ТАК БЫЛО У МЕНЯ!!!
    # """
    #     """Тест кэширования страницы index.html"""
    #     first_state = self.authorized_client.get(reverse('posts:index'))
    #     post_1 = Post.objects.get(pk=1)
    #     post_1.text = 'Измененный текст'
    #     post_1.save()
    #     second_state = self.authorized_client.get(reverse('posts:index'))
    #     self.assertEqual(first_state.content, second_state.content)
    #     cache.clear()
    #     third_state = self.authorized_client.get(reverse('posts:index'))
    #     self.assertNotEqual(first_state.content, third_state.content)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT,
                      ignore_errors=True)
        super().tearDownClass()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_name',)

        COUNT_OF_POST = 13
        cls.group = Group.objects.create(
            title='Заголовок для тестовой группы',
            slug='test_slug2',
            description='Тестовое описание'
        )

        cls.post = Post.objects.bulk_create(
            [
                Post(
                    text=f'Тестовый пост {i}',
                    author=cls.author,
                    group=cls.group
                ) for i in range(COUNT_OF_POST)
            ]
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='VitaGor')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)


    def test_first_page_contains_ten_posts(self):
        COEFF_POSTS_PER_PAGE_1 = 10
        list_urls = {
            reverse("posts:index"): "posts/index.html",
            reverse("posts:group_list", kwargs={
                "slug": self.group.slug
            }): "group"
        }
        for tested_url in list_urls.keys():
            response = self.client.get(tested_url)
            self.assertEqual(
                len(response.context['page_obj']),
                COEFF_POSTS_PER_PAGE_1
            )

    def test_second_page_contains_three_posts(self):
        COEFF_POSTS_PER_PAGE_2 = 3

        list_urls = {
            reverse("posts:index") + "?page=2": "index",
            reverse("posts:group_list", kwargs={
                "slug": self.group.slug
            }) + "?page=2":
                "group",
        }
        for tested_url in list_urls.keys():
            response = self.client.get(tested_url)
            self.assertEqual(
                len(response.context['page_obj']),
                COEFF_POSTS_PER_PAGE_2
            )

    # def test_profile_page_context_with_image(self):
    #     response = self.authorized_client.get(
    #         reverse('posts:profile', args=[self.user])
    #     )
    #     self.authorized_client.post(
    #         reverse("posts:profile_follow", args=(self.user.username,)),
    #     )
    #     self.assertIn('page_obj', response.context)
    #     first_object = response.context['page_obj'][0].image
    #     self.assertEqual(first_object.image, 'posts/small.gif')


class FollowViewsTest(TestCase):
    def setUp(self):
        self.client_auth_follower = Client()
        self.client_auth_following = Client()
        self.user_follower = User.objects.create_user(username='follower',
                                                      email='test_11@mail.ru',
                                                      password='test_pass')
        self.user_following = User.objects.create_user(username='following',
                                                       email='test22@mail.ru',
                                                       password='test_pass')
        self.post = Post.objects.create(
            author=self.user_following,
            text='Тестовая запись для тестирования ленты'
        )
        self.client_auth_follower.force_login(self.user_follower)
        self.client_auth_following.force_login(self.user_following)

    def test_follow(self):
        self.client_auth_follower.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user_following.username})
        )
        self.assertEqual(Follow.objects.all().count(), 1)

    def test_unfollow(self):
        self.client_auth_follower.get(reverse('posts:profile_follow',
                                      kwargs={'username': self.user_following.
                                              username}))
        self.client_auth_follower.get(reverse('posts:profile_unfollow',
                                      kwargs={'username': self.user_following.
                                              username}))
        self.assertEqual(Follow.objects.all().count(), 0)

    def test_subscription_feed(self):
        """запись появляется в ленте подписчиков"""

        Follow.objects.create(user=self.user_follower,
                              author=self.user_following)
        response = self.client_auth_follower.get('/follow/')
        post_text_0 = response.context["page_obj"][0].text
        self.assertEqual(post_text_0, 'Тестовая запись для тестирования ленты')
        # в качестве неподписанного пользователя проверяем собственную ленту
        response = self.client_auth_following.get('/follow/')
        self.assertNotContains(response,
                               'Тестовая запись для тестирования ленты')

    # def test_add_comment(self):
    #     self.client_auth_following.post(f'/following/{self.post.id}/comment',
    #                                     {'text': "тестовый комментарий"},
    #                                     follow=True)
    #     response = self.client_auth_following.get(
    #         f'/following/{self.post.id}/'
    #     )
    #     self.assertContains(response, 'тестовый комментарий')
    #     self.client_auth_following.logout()
    #     self.client_auth_following.post(
    #         f'/following/{self.post.id}/comment',
    #         {'text': "комментарий от гостя"},
    #         follow=True
    #     )
    #     response = self.client_auth_following.get(
    #         f'/following/{self.post.id}/'
    #     )
    #     self.assertNotContains(response, 'комментарий от гостя')


# class CacheTests(TestCase):
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         cls.post = Post.objects.create(
#             author=User.objects.create_user(username='test_name',
#                                             email='test@mail.ru',
#                                             password='test_pass', ),
#             text='Тестовая запись для создания поста')
#
#     def setUp(self):
#         self.guest_client = Client()
#         self.user = User.objects.create_user(username='VitaGor')
#         self.authorized_client = Client()
#         self.authorized_client.force_login(self.user)

    # def test_cache_index(self):
    #     """Тест кэширования страницы index.html"""
    #     first_state = self.authorized_client.get(reverse('posts:index'))
    #     post_1 = Post.objects.get(pk=1)
    #     post_1.text = 'Измененный текст'
    #     post_1.save()
    #     second_state = self.authorized_client.get(reverse('posts:index'))
    #     self.assertEqual(first_state.content, second_state.content)
    #     cache.clear()
    #     third_state = self.authorized_client.get(reverse('posts:index'))
    #     self.assertNotEqual(first_state.content, third_state.content)

