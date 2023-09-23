import pytest
from django.conf import settings
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.usefixtures('multi_news')
def test_news_count(client):
    '''Считает кол-во новостей на гл. стр.'''
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
@pytest.mark.usefixtures('multi_news')
def test_news_order(client):
    '''Проверяет сортировку новостей на гл.стр. от свежих к старым.'''
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
@pytest.mark.usefixtures('multi_comment')
def test_comments_order(admin_client, new):
    '''Проверяет сортировку комментариев от старых к новым.'''
    url = reverse('news:detail', args=(new.pk,))
    response = admin_client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, new):
    '''Форма отправки комментария не доступна анонимному польз-лю.'''
    url = reverse('news:detail', args=(new.pk,))
    response = client.get(url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(admin_client, new):
    '''Форма отправки комментария доступна авторизованному польз-лю.'''
    url = reverse('news:detail', args=(new.pk,))
    response = admin_client.get(url)
    assert 'form' in response.context
