import pytest
from django.utils import timezone
from django.contrib.auth import get_user_model
from blog.models import Post, Rate
from blog.tasks import calculate_post_total_rates_amount, calculate_post_average_rating_speed
import random

User = get_user_model()


@pytest.mark.django_db
class TestRateWeightCalculation:
    def test_rate_weight_calculation_average_rating_speed(self):
        # Create a post 30 days ago
        post = Post.objects.create(
            title='Test Post',
            content='Content of test post',
            created_at=timezone.now() - timezone.timedelta(days=30)
        )

        # Create multiple users
        users = [User.objects.create_user(username=f'user{i}', password='password') for i in range(300)]

        user_part_1 = users[0:201]

        # Create approximately 200 rates over the past 30 days with weight 1
        for user in user_part_1:
            days_ago = random.randint(0, 30)
            created_at = timezone.now() - timezone.timedelta(days=days_ago)
            score = random.randint(1, 5)
            rate = Rate.objects.create(
                post=post,
                user=user,
                score=score,
                created_at=created_at,
                weight=1
            )
            rate.save()
        post.refresh_from_db()
        # Calculate normal rating speed during 30 days
        post.calculate_average_rating_speed()

        # Consider weighted avg is equal to normal avg (all rates weights are equal to 1)
        post.weighted_total_rates_sum = post.total_rates_sum
        post.weighted_rates_count = post.rates_count
        post.save()

        post.refresh_from_db()

        initial_weighted_average_rate = post.weighted_average_rate

        # Calculate normal average rate
        initial_normal_average_rate = post.normal_average_rate

        user_part_2 = users[201:300]

        # Create 100 rates in the last hour
        for user in user_part_2:
            score = random.randint(1, 5)
            rate = Rate.objects.create(
                post=post,
                user=user,
                score=score,
                created_at=timezone.now() - timezone.timedelta(minutes=random.randint(0, 60))
            )
            rate.save()

        # Run the task to calculate weighted rates after recent high volume of ratings
        calculate_post_total_rates_amount()

        # Refresh post data
        post.refresh_from_db()

        # Calculate weighted average rate after recent high volume of ratings
        final_weighted_average_rate = post.weighted_average_rate

        # Calculate normal average rate after recent high volume of ratings
        final_normal_average_rate = post.normal_average_rate

        print(f'Initial Normal Average Rate: {initial_normal_average_rate}')
        print(f'Initial Weighted Average Rate: {initial_weighted_average_rate}')
        print(f'Final Weighted Average Rate: {final_weighted_average_rate}')
        print(f'Final Normal Average Rate: {final_normal_average_rate}')

        assert 0 <= initial_weighted_average_rate <= 5, 'Initial weighted average rate is out of bounds (0-5)'
        assert 0 <= final_weighted_average_rate <= 5, 'Final weighted average rate is out of bounds (0-5)'
        assert 0 <= initial_normal_average_rate <= 5, 'Initial Normal average rate is out of bounds (0-5)'
        assert 0 <= final_normal_average_rate <= 5, 'Final Normal average rate is out of bounds (0-5)'

        # Compare normal and weighted average rate
        assert (
            abs(final_normal_average_rate - initial_normal_average_rate) >
            abs(final_weighted_average_rate - initial_weighted_average_rate),
            'Difference of initial normal average and final normal average should be more than'
            ' difference of initial weighted average and final weighted average')

        assert initial_weighted_average_rate != final_weighted_average_rate, \
            'Initial and final weighted average rates should differ after recent high volume of ratings'

    def test_rate_weight_calculation_standard_deviation(self):
        # Create a post 30 days ago
        post = Post.objects.create(
            title='Test Post',
            content='Content of test post',
            created_at=timezone.now() - timezone.timedelta(days=30)
        )

        # Create multiple users
        users = [User.objects.create_user(username=f'user{i}', password='password') for i in range(1002)]

        user_part_1 = users[0:1000]

        # Create approximately 200 rates over the past 30 days with weight 1
        for user in user_part_1:
            days_ago = random.randint(0, 30)
            created_at = timezone.now() - timezone.timedelta(days=days_ago)
            score = random.randint(4, 5)
            rate = Rate.objects.create(
                post=post,
                user=user,
                score=score,
                created_at=created_at,
                weight=1
            )
            rate.save()
        post.refresh_from_db()

        first_user = users[1000]
        second_user = users[1001]

        # Create rate with score in standard range (like all before scores in range (3, 5))
        first_score = 4
        first_rate = Rate.objects.create(
            post=post,
            user=first_user,
            score=first_score,
            created_at=timezone.now() - timezone.timedelta(minutes=random.randint(0, 60))
        )
        first_rate.save()

        # Create rate with score out of standard range (all before scores are in range (3, 5))
        second_score = 0
        second_rate = Rate.objects.create(
            post=post,
            user=second_user,
            score=second_score,
            created_at=timezone.now() - timezone.timedelta(minutes=random.randint(0, 60))
        )
        second_rate.save()

        # Run the task to calculate weighted rates and rate weight after creating last rate
        calculate_post_total_rates_amount()

        # Refresh post data
        post.refresh_from_db()

        # Refresh first_rate data
        first_rate.refresh_from_db()

        # Refresh second_rate data
        second_rate.refresh_from_db()

        # check if first_rate is outlier
        first_rate_is_outlier = first_rate.is_outlier

        # check if second_rate is outlier
        second_rate_is_outlier = second_rate.is_outlier

        # check first_rate weight
        first_rate_weight = first_rate.weight

        # check second_rate weight
        second_rate_weight = second_rate.weight

        print(f'Is First Rate Outlier: {first_rate_is_outlier}')
        print(f'Is Second Rate Outlier: {second_rate_is_outlier}')

        assert 0 <= first_rate_weight <= 1, 'First rate weight is out of bounds (0-1)'
        assert second_rate_weight == 0, 'second rate weight is not 0'
        assert first_rate_is_outlier is False, 'First rate is outlier'
        assert second_rate_is_outlier is True, 'Second rate is not outlier'

