from datetime import datetime

import pytest
from django.test.client import Client

from news.models import News, Comment
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='BIBA')


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='BOBA')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news():
    return News.objects.create(
        title='Заголовок',
        text='Текст новости',
        date=datetime.today()
    )


@pytest.fixture
def create_news():
    news_list = []
    for i in range(NEWS_COUNT_ON_HOME_PAGE):
        news = News.objects.create(
            title=f'Test News {i}',
            text=f'Test content {i}',
            date=datetime.today()
        )
        news_list.append(news)
    return news_list


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'

    )


@pytest.fixture
def create_comment(author):
    news = News.objects.create(
        title='Test News',
        text='Test content',
        date=datetime.today()
    )

    comment_list = []
    for i in range(NEWS_COUNT_ON_HOME_PAGE):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Test comment {i}'
        )
        comment_list.append(comment)

    return comment_list


@pytest.fixture
def pk_news(news):
    return (news.pk,)


@pytest.fixture
def pk_comment(comment):
    return (comment.pk,)


@pytest.fixture
def comment_form():
    return {'text': 'Test comment'}


@pytest.fixture
def edit_form():
    return {'text': 'Update text'}
