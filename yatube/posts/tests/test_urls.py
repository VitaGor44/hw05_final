from django.test import TestCase, Client
from http import HTTPStatus
from django.urls import reverse

from ..models import Group, Post, User

POST_TEXT_MULTIPLY = 15


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            first_name='test_name',
            last_name='test_family_name',
            username='test_user',
            email='test@mail.ru'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тест | Описание группы'
        )
        cls.post = Post.objects.create(
            text='Тестовая запись нового поста' * POST_TEXT_MULTIPLY,
            author=cls.user,
            group=cls.group
        )

        cls.public_urls = {
            '/': 'posts/index.html',
            f'/group/{cls.group.slug}/': 'posts/group_list.html',
            f'/profile/{cls.user.username}/': 'posts/profile.html',
            f'/posts/{cls.post.id}/': 'posts/post_detail.html'
        }
        cls.private_urls = {
            f'/posts/{cls.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html'
        }

    def setUp(self):
        self.guest_client = Client()
        self.user = PostURLTests.user
        self.authorized_client = Client()
        self.another_authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.another_user = User.objects.create_user(username='HasNoName')

    def test_url(self):
        """url → valid status code"""
        # group = PostURLTests.group
        user = PostURLTests.user
        response_index = self.guest_client.get('/')
        response_slug = self.guest_client.get(f'/group/{self.group.title}/')
        response_new = self.authorized_client.get('/create/')
        response_404 = self.guest_client.get('/unknown/page/')
        response_non_exist = self.authorized_client.get(
            f'/{user.username}/unknown/edit/'
        )

        test_dict = {
            response_index.status_code: HTTPStatus.OK,
            response_slug.status_code: HTTPStatus.OK,
            response_new.status_code: HTTPStatus.OK,
            response_404.status_code: HTTPStatus.NOT_FOUND,
            response_non_exist.status_code: HTTPStatus.NOT_FOUND,
        }

        for value, expected in test_dict.items():
            with self.subTest(value=value):
                self.assertEquals(value, expected)

    def test_new_url_redirect_anonymous(self):
        """Страница /create/ перенаправляет анонимного пользователя."""
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_private_url_use_right_template(self):
        """Использование URL-адресом шаблона приватных адресов."""
        for address, template in self.private_urls.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(
                    response,
                    template,
                    f'Страница {address} использует неправильный шаблон'
                )

    def test_urls_use_right_template(self):
        """Использование URL-адресом шаблона публичных адресов."""
        for address, template in self.public_urls.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(
                    response,
                    template,
                    f'Страница {address} использует неправильный шаблон'
                )

    def test_new_for_authorized(self):
        """Страница /create доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_detail_guest_client(self):
        response = self.guest_client.get(
            reverse('posts:post_create')
        )
        self.assertRedirects(response,
                             '/auth/login/?next=/create/')

    def test_redirect_non_author(self):
        """Проверка redirect, если пользователь хочет изменить чужой пост."""
        response = self.another_authorized_client.get(
            f'/posts/{self.post.id}/edit/'
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_page_404(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
