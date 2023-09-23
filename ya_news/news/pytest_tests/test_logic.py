from http import HTTPStatus

import pytest
from django.urls import reverse
from news.models import Comment
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, new, form_data):
    '''Анонимный польз-тель не может оставить комментарий.'''
    url = reverse('news:detail', kwargs={'pk': new.pk})
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_can_create_comment(admin_client, new, form_data):
    '''Авторизованный польз-тель может оставить комментарий.'''
    url = reverse('news:detail', kwargs={'pk': new.pk})
    admin_client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, new, form_data_bad_words):
    url = reverse('news:detail', kwargs={'pk': new.pk})
    author_client.post(url, data=form_data_bad_words)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, new, comment):
    '''Автор может удалить свой комментарий.'''
    url = reverse('news:delete', kwargs={'pk': new.pk})
    response = author_client.delete(url)
    expected_url = reverse(
        'news:detail',
        kwargs={'pk': comment.news.pk}
    ) + '#comments'
    assertRedirects(response, expected_url)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_author_can_apdate_comment(author_client, new, comment, form_data):
    '''Автор может редактировать свой комментарий.'''
    url = reverse('news:edit', kwargs={'pk': new.pk})
    response = author_client.post(url, data=form_data)
    expected_url = reverse(
        'news:detail',
        kwargs={'pk': comment.news.pk}
    ) + '#comments'
    assertRedirects(response, expected_url)
    comments_count = Comment.objects.count()
    assert comments_count == 1


@pytest.mark.django_db
@pytest.mark.usefixtures('comment')
def test_user_cant_delete_comment(admin_client, new):
    '''Польз-тель не может удалить чужой комментарий.'''
    url = reverse('news:delete', kwargs={'pk': new.pk})
    response = admin_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


@pytest.mark.django_db
def test_user_cant_update_comment(admin_client, new, comment, form_data):
    '''Польз-тель не может редактировать чужой комментарий.'''
    url = reverse('news:delete', kwargs={'pk': new.pk})
    response = admin_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comment.text != form_data['text']
