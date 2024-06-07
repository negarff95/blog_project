import pytest
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestUserModel:
    def test_create_user(self):
        user = User.objects.create_user(username='test_user', password='password')
        assert user.username == 'test_user'
        assert not user.is_staff
        assert not user.is_superuser
        assert user.check_password('password')

    def test_create_staff(self):
        staff_user = User.objects.create_staff(username='staff_user', password='password')
        assert staff_user.username == 'staff_user'
        assert staff_user.is_staff
        assert not staff_user.is_superuser
        assert staff_user.check_password('password')

    def test_create_superuser(self):
        superuser = User.objects.create_superuser(username='superuser', password='password')
        assert superuser.username == 'superuser'
        assert superuser.is_staff
        assert superuser.is_superuser
        assert superuser.check_password('password')

    def test_increase_rates_count(self):
        user = User.objects.create_user(username='test_user', password='password')
        user.increase_rates_count(5)
        assert user.rates_count == 5

    def test_increase_total_rates_weight(self):
        user = User.objects.create_user(username='test_user', password='password')
        user.increase_total_rates_weight(0.5)
        assert user.total_rates_weight == 0.5

    def test_account_age(self):
        user = User.objects.create_user(username='test_user', password='password')
        user.created_at = timezone.now() - timezone.timedelta(days=10)
        user.save()
        assert user.account_age == 10

    def test_rate_quality(self):
        user = User.objects.create_user(username='test_user', password='password', rates_count=10, total_rates_weight=3)
        assert user.rate_quality == 0.3

    def test_account_weight(self):
        new_user = User.objects.create_user(username='test_user_1', password='password', rates_count=5)
        older_user = User.objects.create_user(username='test_user_2', password='password')
        older_user.created_at = timezone.now() - timezone.timedelta(days=35)
        older_user.save()

        assert new_user.account_weight == 0.1
        assert older_user.account_weight == 0.2

    def test_calculate_rate_weight(self):
        user = User.objects.create_user(username='test_user', password='password', rates_count=5, total_rates_weight=1)
        user.calculate_rate_weight()
        assert round(user.rate_weight, 2) == 0.15
