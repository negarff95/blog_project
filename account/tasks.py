import datetime
from account.models import User
from blog_project.celery import app


@app.task(name="user_rate_weight", autoregister=True)
def user_rate_weight():
    """
    calculate user rate weight for users (which has rates in past 24 hours) every 24 hours
    """
    day_before = datetime.datetime.now() - datetime.timedelta(days=1)

    users = User.objects.filter(rates__created_at__gte=day_before)

    for user in users:
        user.calculate_rate_weight()



