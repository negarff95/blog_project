import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken
from account.models import User
from blog.models import Post, Rate
from blog.serializers import RateSerializer, PostSerializer
from blog.views import RateView


@pytest.mark.django_db
class TestPostListView:
    def test_post_list_view(self):
        client = APIClient()
        url = reverse('post_list')
        response = client.get(url)
        assert response.status_code == 200

@pytest.mark.django_db
class TestSubmitRateView:
    def test_submit_rate_view(self):
        RateView.throttle_classes = []  # UserRateThrottle caches the data so should be disabled
        authorized_user = User.objects.create(username='authorized_user', password='testpassword')
        unauthorized_user = User.objects.create(username='unauthorized_user', password='testpassword')
        post = Post.objects.create(title='Test Post', content='Content of test post')

        # authorized user
        access_token = AccessToken.for_user(authorized_user)
        authorized_client = APIClient()
        authorized_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # unauthorized user
        unauthorized_client = APIClient()

        url = reverse('submit_rate')
        data = {'post': post.id, 'score': 5}

        authorized_response = authorized_client.post(url, data, format='json')
        unauthorized_response = unauthorized_client.post(url, data, format='json')

        assert authorized_response.status_code == 200
        assert Rate.objects.filter(post=post, user=authorized_user).exists()

        assert unauthorized_response.status_code == 401
        assert not Rate.objects.filter(post=post, user=unauthorized_user).exists()

@pytest.mark.django_db
class TestPostSerializer:
    def test_post_serializer(self):
        post = Post.objects.create(title='Test Post', content='Content of test post')
        serializer = PostSerializer(post)
        data = serializer.data
        assert data['title'] == post.title
        assert data['average_rate'] is None
        assert data['rate_counts'] == 0

@pytest.mark.django_db
class TestRateSerializer:
    def test_rate_serializer(self):
        user = User.objects.create(username='testuser', password='testpassword')
        post = Post.objects.create(title='Test Post', content='Content of test post')
        data = {'post': post.id, 'score': 5}
        serializer = RateSerializer(data=data, context={'user': user})
        assert serializer.is_valid()
        rate = serializer.save()
        assert rate.post == post
        assert rate.user == user
        assert rate.score == 5
