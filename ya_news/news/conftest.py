from datetime import datetime, timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from news.forms import BAD_WORDS
from news.models import Comment, News

url_home = reverse('news:home')


@pytest.fixture
def new():
    '''Создание новости.'''
    return News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )


@pytest.fixture
def comment(author, new):
    '''Создание комментария.'''
    return Comment.objects.create(
        text='Текст комментария',
        created=datetime.today(),
        author=author,
        news=new
    )


@pytest.fixture
def multi_comment(new, author):
    '''Создает N-комментариев.'''
    today = timezone.now()
    for index in range(2):
        all_comments = Comment.objects.create(
            text=f'Текст{index}',
            author=author,
            news=new,
            created=today
        )
        all_comments.created = today + timedelta(hours=index)
        all_comments.save()
    return all_comments


@pytest.fixture
def author(django_user_model):
    '''Создание автора.'''
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    '''Логиним автора.'''
    client.force_login(author)
    return client


@pytest.fixture
def multi_news():
    '''Создает N-новостей.'''
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index),
        )
        for index in range(12)
    ]
    return News.objects.bulk_create(all_news)


@pytest.fixture
def form_data(new):
    return {
        'text': 'ТекстТекст',
        'news': new}


@pytest.fixture
def form_data_bad_words():
    return {'text': f'Текст {BAD_WORDS[0]} Текст'}
