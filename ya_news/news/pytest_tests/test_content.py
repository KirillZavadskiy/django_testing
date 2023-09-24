import pytest
from django.conf import settings
from django.urls import reverse

from news.conftest import url_home
from news.forms import CommentForm


@pytest.mark.django_db
@pytest.mark.usefixtures('multi_news')
def test_news_count(client):
    '''Считает кол-во новостей на гл. стр.'''
    response = client.get(url_home)
    news = response.context['object_list']
    news_count = len(news)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
@pytest.mark.usefixtures('multi_news')
def test_news_order(client):
    '''Проверяет сортировку новостей на гл.стр. от свежих к старым.'''
    url = reverse('news:home')
    response = client.get(url)
    all_news = response.context['object_list']
    all_dates = [news.date for news in all_news]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
@pytest.mark.usefixtures('multi_comment')
def test_comments_order(admin_client, new):
    '''Проверяет сортировку комментариев от старых к новым.'''
    url = reverse('news:detail', args=(new.pk,))
    response = admin_client.get(url)
    assert 'news' in response.context
    one_new = response.context['news']
    comments = one_new.comment_set.all()
    all_dates = [comment.created for comment in comments]
    sorted_dates = sorted(all_dates)
    assert all_dates == sorted_dates


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, new_in_list',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('admin_client'), True),
    )
)
def test_client_has_form(parametrized_client, new_in_list, new):
    '''Форма отправки комментария доступна автор-нному/аноним-ому польз-лю.'''
    url = reverse('news:detail', args=(new.pk,))
    response = parametrized_client.get(url)
    assert ('form' in response.context) is new_in_list
    if new_in_list:
        assert isinstance(response.context['form'], CommentForm)
