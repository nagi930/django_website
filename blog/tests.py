from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post
from django.utils import timezone
from django.contrib.auth.models import User

# Create your tests here.
class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.author_000 = User.objects.create(username='user', password='password')

    def test_post_list(self):
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title

        print(title.text)

        self.assertEqual(title.text, 'Blog')

        navbar = soup.find('div', id='navbar')
        self.assertIn('Blog', navbar.text)
        self.assertIn('About me', navbar.text)

        self.assertEqual(Post.objects.count(), 0)
        self.assertIn('아직 게시물이 없습니다.', soup.body.text)

        post_000 = Post.objects.create(
            title = 'The first post',
            content = 'Hello World',
            created = timezone.now(),
            author = self.author_000
        )

        self.assertGreater(Post.objects.count(), 0)

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        body = soup.body
        self.assertNotIn('아직 게시물이 없습니다.', soup.body.text)
        self.assertIn(post_000.title, body.text)

    def test_post_detail(self):
        post_000 = Post.objects.create(
            title='The first post',
            content='Hello World',
            created=timezone.now(),
            author=self.author_000
        )

        self.assertGreater(Post.objects.count(), 0)

        post_000_url = post_000.get_absolute_url()
        self.assertEqual(post_000_url, '/blog/{}'.format(post_000.pk))
