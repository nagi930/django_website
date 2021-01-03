from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post, Category, Tag, Comment
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

def create_tag(name='economy'):
    tag, is_created = Tag.objects.get_or_create(
        name=name
    )
    tag.slug = tag.name.replace(' ', '-').replace('/', '')
    tag.save()

    return tag

def create_post(title, content, author, category=None):
    blog_post = Post.objects.create(
        title=title,
        content=content,
        created=timezone.now(),
        author=author,
        category=category
    )

    return blog_post

def create_comment(post, text='a comment', author=None):
    if author is None:
        author, is_created = User.objects.get_or_create(
            username='guest',
            password='guestpassword'
        )

    comment = Comment.objects.create(
        post=post,
        text=text,
        author=author
    )
    return comment


class TestModel(TestCase):
    def setUp(self):
        self.client = Client()
        self.author_000 = User.objects.create_user(username='smith', password='password')

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

    def test_tag(self):
        tag_000 = create_tag(name='bad_guy')
        tag_001 = create_tag(name='america')

        post_000 = create_post(
            title='The first post',
            content='Hello World',
            author=self.author_000,
        )

        post_000.tags.add(tag_000)
        post_000.tags.add(tag_001)
        post_000.save()

        post_001 = create_post(
            title='The second post',
            content='Hello World2',
            author=self.author_000,
        )

        post_001.tags.add(tag_001)
        post_001.save()

        self.assertEqual(post_000.tags.count(), 2)
        self.assertEqual(tag_001.post_set.count(), 2)
        self.assertEqual(tag_001.post_set.first(), post_000)
        self.assertEqual(tag_001.post_set.last(), post_001)

    def test_comment(self):
        post_000 = create_post(
            title='The first post',
            content='Hello World',
            author=self.author_000,
        )

        self.assertEqual(Comment.objects.count(), 0)

        comment_000 = create_comment(
            post=post_000,
            text='first text'
        )

        comment_001 = create_comment(
            post=post_000,
            text='second text'
        )
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(post_000.comment_set.count(), 2)







class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.author_000 = User.objects.create_user(username='smith', password='password')
        self.user_obama = User.objects.create_user(username='obama', password='password')

    def check_navbar(self, soup):
        navbar = soup.find('div', id='navbar')
        self.assertIn('Blog', navbar.text)
        self.assertIn('About me', navbar.text)

    def check_right_side(self, soup):
        category_card = soup.find('div', id='category-card')
        self.assertIn('미분류', category_card.text)
        self.assertIn('News', category_card.text)




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
        tag_america = create_tag(name='america')

        post_000 = create_post(
            title = 'The first post',
            content = 'Hello World',
            author = self.author_000
        )

        post_000.tags.add(tag_america)
        post_000.save()

        post_001 = create_post(
            title='The second post',
            content='Hello World2',
            author=self.author_000,
            category=create_category(name='News')
        )

        post_001.tags.add(tag_america)
        post_001.save()


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

        # Tag
        post_card_000 = main_div.find('div', id='post-card-{}'.format(post_000.pk))
        # self.assertIn('#america', post_card_000)




    def test_post_detail(self):
        category_news = create_category(name='News')
        post_000 = create_post(
            title='The first post',
            content='Hello World',
            author=self.author_000,
            category = create_category(name='News')
        )

        comment_000 = create_comment(post_000, text='test comment', author=self.user_obama)
        comment_001 = create_comment(post_000, text='test comment2', author=self.author_000)

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

        # Comment
        comments_div = main_div.find('div', id='comments-list')
        self.assertIn(comment_000.author.username, comments_div.text)
        self.assertIn(comment_000.text, comments_div.text)

        # Tag
        # tag_america = create_tag(name='america')
        # post_000.tags.add(tag_america)
        # post_000.save()
        # self.assertIn('#america', main_div)


        self.assertIn(category_news.name, main_div.text)
        self.assertNotIn('EDIT', main_div.text)

        login_success = self.client.login(username='smith', password='password')
        self.assertTrue(login_success)
        response = self.client.get(post_000_url)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        main_div = soup.find('div', id='main-div')
        self.assertEqual(post_000.author, self.author_000)
        self.assertIn('EDIT', main_div.text)

        login_success = self.client.login(username='obama', password='password')
        self.assertTrue(login_success)
        response = self.client.get(post_000_url)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        main_div = soup.find('div', id='main-div')
        self.assertEqual(post_000.author, self.author_000)
        self.assertNotIn('EDIT', main_div.text)

        comments_div = main_div.find('div', id='comments-list')
        comment_000_div = comments_div.find('div', id='comment-id-{}'.format(comment_000.pk))
        self.assertIn('edit', comment_000_div.text)
        self.assertIn('delete', comment_000_div.text)

        comment_001_div = comments_div.find('div', id='comment-id-{}'.format(comment_001.pk))
        self.assertNotIn('edit', comment_001_div.text)
        self.assertNotIn('delete', comment_001_div.text)

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

    def test_tag_page(self):
        tag_000 = create_tag(name='bad_guy')
        tag_001 = create_tag(name='america')

        post_000 = create_post(
            title='The first post',
            content='Hello World',
            author=self.author_000,
        )

        post_000.tags.add(tag_000)
        post_000.tags.add(tag_001)
        post_000.save()

        post_001 = create_post(
            title='The second post',
            content='Hello World2',
            author=self.author_000,
        )

        post_001.tags.add(tag_001)
        post_001.save()

        response = self.client.get(tag_000.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        main_div = soup.find('div', id='main-div')
        self.assertIn(post_000.title, main_div.text)
        self.assertNotIn(post_001.title, main_div.text)

        blog_h1 = main_div.find('h1', id='blog-list-title')
        self.assertIn('#{}'.format(tag_000.name), blog_h1.text)

    def test_post_create(self):
        response = self.client.get('/blog/create/')
        # self.assertEqual(response.status_code, 200)

        self.client.login(username='smith', password='password')
        response = self.client.get('/blog/create/')
        self.assertEqual(response.status_code, 200)


    def test_post_update(self):
        response = self.client.get('/blog/create/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        main_div = soup.find('div', id='main-div')





    def test_post_update(self):
        post_000 = create_post(
            title='The first post',
            content='Hello World',
            author=self.author_000,
        )

        self.assertEqual(post_000.get_update_url(), post_000.get_absolute_url() + 'update/')
        response = self.client.get(post_000.get_update_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        main_div = soup.find('div', id='main-div')
        self.assertNotIn('Created', main_div.text)
        self.assertNotIn('Author', main_div.text)

    def test_new_comment(self):
        post_000 = create_post(
            title='The first post',
            content='Hello World',
            author=self.author_000,
        )
        login_success = self.client.login(username='smith', password='password')
        self.assertTrue(login_success)

        response = self.client.post(
            post_000.get_absolute_url() + 'new_comment/', {'text' : 'A test comment'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        main_div = soup.find('div', id='main-div')
        self.assertIn(post_000.title, main_div.text)
        self.assertIn('A test comment', main_div.text)




