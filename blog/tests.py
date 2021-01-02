from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post, Category
from django.utils import timezone
from django.contrib.auth.models import User


def create_category(name='life', description=''):
    category, is_created = Category.objects.get_or_create(
        name=name,
        description=description
    )

    category.slug = category.name.replace(' ', '-').replace('/', '')
    category.save()

    return category

def create_post(title, content, author, category=None):
    blog_post = Post.objects.create(
        title=title,
        content=content,
        created=timezone.now(),
        author=author,
        category=category
    )

    return blog_post



class TestModel(TestCase):
    def setUp(self):
        self.client = Client()
        self.author_000 = User.objects.create(username='user', password='password')

    def test_category(self):
        category = create_category()
        post_000 = create_post(
            title='The first post',
            content='Hello World',
            author=self.author_000,
            category=category
        )

        self.assertEqual(category.post_set.count(), 1)


        def test_post(self):
            post_000 = create_post(
                title='The first post',
                content='Hello World',
                author=self.author_000,
                category=category
            )



class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.author_000 = User.objects.create(username='user', password='password')

    def check_navbar(self, soup):
        navbar = soup.find('div', id='navbar')
        self.assertIn('Blog', navbar.text)
        self.assertIn('About me', navbar.text)

    def check_right_side(self, soup):
        category_card = soup.find('div', id='category-card')
        self.assertIn('미분류(1)', category_card.text)
        self.assertIn('News(1)', category_card.text)




    def test_post_list_no_post(self):
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title

        print(title.text)

        self.assertIn(title.text, 'Blog')

        self.check_navbar(soup)
        # navbar = soup.find('div', id='navbar')
        # self.assertEqual(Post.objects.count(), 0)
        # self.assertIn('아직 게시물이 없습니다.', soup.body.text)


    def test_post_list_with_post(self):

        post_000 = create_post(
            title = 'The first post',
            content = 'Hello World',
            author = self.author_000
        )

        post_001 = create_post(
            title='The second post',
            content='Hello World2',
            author=self.author_000,
            category=create_category(name='News')
        )

        self.assertGreater(Post.objects.count(), 0)

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        body = soup.body
        self.assertNotIn('아직 게시물이 없습니다.', soup.body.text)
        self.assertIn(post_000.title, body.text)

        post_000_read_more_bnt = body.find('a', id='read-more-post-{}'.format(post_000.pk))
        self.assertEqual(post_000_read_more_bnt['href'], post_000.get_absolute_url())

        # category card에서
        #### 미분류(1), News(1) 있어야함
        self.check_right_side(soup)

        main_div = soup.find('div', id='main-div')
        self.assertIn('News', main_div.text)
        self.assertIn('미분류', main_div.text)

    def test_post_detail(self):
        post_000 = create_post(
            title='The first post',
            content='Hello World',
            author=self.author_000
        )

        post_001 = create_post(
            title='The second post',
            content='Hello World2',
            author=self.author_000,
            category=create_category(name='News')
        )

        self.assertGreater(Post.objects.count(), 0)

        post_000_url = post_000.get_absolute_url()
        self.assertEqual(post_000_url, '/blog/{}/'.format(post_000.pk))

        response = self.client.get(post_000_url)

        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title

        self.assertEqual(title.text, '{} - Blog'.format(post_000.title))

        self.check_navbar(soup)

        body = soup.body
        main_div = body.find('div', id='main-div')
        self.assertIn(post_000.title, main_div.text)
        self.assertIn(post_000.author.username, main_div.text)
        self.assertIn(post_000.content, main_div.text)
        self.check_right_side(soup)

    def test_post_list_by_category(self):
        category_news = create_category(name='News')

        post_000 = create_post(
            title='The first post',
            content='Hello World',
            author=self.author_000
        )

        post_001 = create_post(
            title='The second post',
            content='Hello World2',
            author=self.author_000,
            category=category_news
        )

        response = self.client.get(category_news.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual('Blog - {}'.format(category_news.name), soup.title.text)

        main_div = soup.find('div', id='main-div')
        self.assertNotIn('미분류', main_div.text)
        self.assertIn(category_news.name, main_div.text)

    def test_post_list_no_category(self):
        category_news = create_category(name='News')

        post_000 = create_post(
            title='The first post',
            content='Hello World',
            author=self.author_000
        )

        post_001 = create_post(
            title='The second post',
            content='Hello World2',
            author=self.author_000,
            category=category_news
        )

        response = self.client.get('/blog/category/_none/')
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')

        main_div = soup.find('div', id='main-div')
        self.assertIn('미분류', main_div.text)
        self.assertNotIn(category_news.name, main_div.text)


