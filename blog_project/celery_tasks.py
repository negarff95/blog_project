from celery.schedules import crontab


CELERY_BEAT_SCHEDULE = {
    'calculate_post_total_rates_amount': {
        'task': 'calculate_post_total_rates_amount',
        'schedule': 18000,
        'options': {'queue': 'periodic_queue'}
    },
    'calculate_post_average_rating_speed': {
        'task': 'calculate_post_average_rating_speed',
        'schedule': 86400,
        'options': {'queue': 'periodic_queue'}
    },
    'user_rate_weight': {
        'task': 'user_rate_weight',
        'schedule': 86400,
        'options': {'queue': 'periodic_queue'}
    }
}
