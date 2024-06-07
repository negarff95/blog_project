import pytest
from blog.models import Post, Rate
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


@pytest.mark.django_db
class TestPostModel:

    def setup_method(self):
        self.user = User.objects.create(username='testuser', password='testpassword')
        self.post = Post.objects.create(title='Test Post', content='Content of test post')

    def test_update_statistics(self):
        self.post.update_statistics(4)
        assert self.post.rates_count == 1
        assert self.post.total_rates_sum == 4

    def test_normal_average_rate(self):
        self.post.update_statistics(4)
        self.post.update_statistics(2)
        assert self.post.normal_average_rate == 3

    def test_standard_deviation(self):
        self.post.update_statistics(4)
        self.post.update_statistics(2)
        assert self.post.standard_deviation == pytest.approx(1.0, 0.001)

    def test_calculate_average_rating_speed(self):
        self.post.created_at = timezone.now() - timezone.timedelta(days=1)
        self.post.save()
        self.post.update_statistics(4)
        self.post.calculate_average_rating_speed()
        assert round(self.post.average_rating_speed, 2) == 0.21



@pytest.mark.django_db
class TestRateModel:

    def setup_method(self):
        self.user = User.objects.create(username='testuser', password='testpassword')
        self.post = Post.objects.create(title='Test Post', content='Content of test post')
        self.rate = Rate.objects.create(post=self.post, user=self.user, score=4)

    def test_get_is_outlier(self):
        assert not self.rate.get_is_outlier()

    def test_calculate_weight(self):
        weight_1 = Rate.calculate_weight(0.5, 0.8, False)
        weight_2 = Rate.calculate_weight(0.5, 0.8, True)
        assert round(weight_1, 2) == 0.7
        assert weight_2 == 0

