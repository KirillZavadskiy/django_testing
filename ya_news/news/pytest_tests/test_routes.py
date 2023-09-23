from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:home', 'users:login', 'users:logout', 'users:signup'),
)
def test_pages_availability_for_anonymous(client, name):
    '''Анонимному польз-лю доступны страницы.'''
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_news_availability_for_anonymous(client, new):
    '''Анонимному польз-лю доступны новости.'''
    url = reverse('news:detail', args=(new.pk,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_comments_availability_for_author(
    author_client, comment, name
):
    '''Автору доступны ред/удал своих коммент-ев.'''
    url = reverse(name, args=(comment.pk,))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_comments_availability_for_anonymous(
    client, comment, name
):
    '''
    Переадресация анонимного польз-теля при переходе на страницу с правами.
    '''
    url = reverse(name, args=(comment.pk,))
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_pages_availability_for_author(
    admin_client, name, comment
):
    '''404 при переходе пользователя на стр ред/удал не своего коммен-рия.'''
    url = reverse(name, args=(comment.pk,))
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
