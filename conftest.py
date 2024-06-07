import pytest
from unittest.mock import patch

@pytest.fixture(autouse=True)
def mock_celery_tasks():
    with patch('blog.tasks.calculate_post_total_rates_amount.delay') as calculate_post_total_rates_amount_task:
        with patch('blog.tasks.calculate_post_average_rating_speed.delay') as calculate_post_average_rating_speed_task:
            with patch('account.tasks.user_rate_weight.delay') as user_rate_weight_task:
                yield calculate_post_total_rates_amount_task, calculate_post_average_rating_speed_task, user_rate_weight_task
