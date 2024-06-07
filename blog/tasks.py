import datetime
from django.db.models import Count
from .models import Rate, Post

from blog_project.celery import app


@app.task(name="calculate_post_total_rates_amount", autoregister=True)
def calculate_post_total_rates_amount():
    """
    Calculate weight of rates created at last {interval_hours} hours and have no weight and
    the total rates amount for each post within a specific time interval
    """
    interval_hours = 5  # Define the time interval for recent rates calculation
    last_hours = datetime.datetime.now() - datetime.timedelta(hours=interval_hours)

    # Retrieve rates within the defined interval, along with related user and post
    rates = Rate.objects.select_related('user', 'post').filter(weight__isnull=True, created_at__gte=last_hours)

    posts_recent_rates_count = rates.values('post').annotate(count=Count('id'))  # Count recent rates for each post

    post_updates = {}
    rate_updates = []

    # Iterate over rates to calculate weight, update post and user attributes
    for rate in rates:
        post = rate.post
        user = rate.user
        post_recent_rates_count = None
        # Check if recent rates count for the post exists, if not, calculate it.
        # to less query to database, all posts' rates count calculated in previous lines with one query to database.
        if post not in post_updates:
            for post_rate in posts_recent_rates_count:
                if post_rate['post'] == post:
                    post_recent_rates_count = post_rate['count']
            if not post_recent_rates_count:
                post_recent_rates_count = rates.filter(post=post).count()

            # Store post updates
            post_updates[post] = {
                'weighted_total_rates_sum': 0,
                'weighted_rates_count': 0,
                'rating_speed_weight': post.get_rating_speed_weight(post_recent_rates_count)
            }

        # Calculate weight, check for outlier, update rate and post attributes
        rating_speed_weight = post_updates[post]['rating_speed_weight']
        user_weight = user.rate_weight
        is_outlier = rate.get_is_outlier(
            post_standard_deviation=post.standard_deviation,
            post_average_rate=post.normal_average_rate,
            post_rates_count=post.rates_count
        )
        weight = rate.calculate_weight(
            rating_speed_weight,
            user_weight,
            is_outlier
        )

        # Store rate updates
        rate.is_outlier = is_outlier
        post_updates[post]['weighted_total_rates_sum'] += rate.score * weight
        post_updates[post]['weighted_rates_count'] += weight
        user.increase_total_rates_weight(weight)
        rate.weight = weight
        rate_updates.append(rate)

    # Bulk update rates with weight and outlier status
    Rate.objects.bulk_update(rate_updates, ['weight', 'is_outlier'])

    # Update posts with weighted total rates sum and weighted rates count
    posts_to_update = []
    for post, data in post_updates.items():
        post.weighted_total_rates_sum += data['weighted_total_rates_sum']
        post.weighted_rates_count += data['weighted_rates_count']
        posts_to_update.append(post)

    # Bulk update posts with weighted attributes
    Post.objects.bulk_update(posts_to_update, ['weighted_total_rates_sum', 'weighted_rates_count'])


@app.task(name="calculate_post_average_rating_speed", autoregister=True)
def calculate_post_average_rating_speed():
    """
    Calculate the average rating speed for each post within a specific time interval
    """
    interval_hours = 24
    last_hours = datetime.datetime.now() - datetime.timedelta(hours=interval_hours)

    # Retrieve posts with rates created within the defined interval
    # to make sure calculating the average rating speed for posts undergoing continuous rating updates
    posts = Post.objects.filter(rates__created_at__gte=last_hours)

    # Iterate over posts to calculate average rating speed
    for post in posts:
        post.calculate_average_rating_speed()
