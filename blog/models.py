from django.utils import timezone

from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.db import models
from django.db.models import F

from account.models import User
from core.models import BaseModel


class Post(BaseModel):
    title = models.CharField(max_length=100)
    content = models.TextField()
    weighted_total_rates_sum = models.FloatField(default=0, validators=[MinValueValidator(0)])
    weighted_rates_count = models.FloatField(default=0, validators=[MinValueValidator(0)])
    rates_count = models.PositiveIntegerField(default=0)
    total_rates_sum = models.PositiveIntegerField(default=0)
    total_rates_sum_squared = models.PositiveIntegerField(default=0)  # Sum of squares of rates
    average_rating_speed = models.FloatField(default=0, validators=[MinValueValidator(0)])

    def __str__(self):
        return self.title

    def update_statistics(self, rate):
        """
        Method to increase basic statistic of post
        """
        self.rates_count += 1
        self.total_rates_sum += rate
        self.total_rates_sum_squared += rate ** 2
        self.save()

    @property
    def normal_average_rate(self):
        if self.rates_count and self.total_rates_sum:
            return round(self.total_rates_sum / self.rates_count, 3)
        return None

    @property
    def standard_deviation(self):
        if self.rates_count == 0:
            return None
        avg = self.normal_average_rate
        variance = (self.total_rates_sum_squared / self.rates_count) - (avg ** 2)
        return round(variance ** 0.5, 3)

    def calculate_average_rating_speed(self):
        """
        Calculate average rating speed for per x hours
        """
        time_diff = (timezone.now() - self.created_at).total_seconds()
        rate_count = self.rates_count

        hours = 5

        if time_diff > 0:
            avg_speed = round(rate_count / (time_diff / (hours * 60 * 60)), 3)  # Ratings per 5 hours
        else:
            avg_speed = rate_count
        self.average_rating_speed = avg_speed
        self.save()

    def get_rating_speed_weight(self, recent_rates_count):
        """
        Calculate a weight based on recent rates count and post's average_rating_speed
        """
        return min(round(self.average_rating_speed / recent_rates_count, 3), 1)

    @property
    def weighted_average_rate(self):
        """
        Calculate weighted average rate based on weighted_total_rates_sum and weighted_rates_count
        """
        if self.weighted_rates_count and self.weighted_total_rates_sum:
            return round(self.weighted_total_rates_sum / self.weighted_rates_count, 3)
        else:
            return None


class Rate(BaseModel):
    post = models.ForeignKey(Post, related_name='rates', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='rates', on_delete=models.CASCADE)
    score = models.PositiveIntegerField(validators=[MaxValueValidator(5)])
    weight = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)], null=True, blank=True)
    is_outlier = models.BooleanField(default=False)

    class Meta:
        unique_together = ('post', 'user')
        indexes = [
            models.Index(fields=['post']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f'{self.post}| {self.user}| {self.score}'

    def get_is_outlier(self, post_standard_deviation=None, post_average_rate=None, post_rates_count=None):
        """
        If total rates count of the post passes min_total_rates_required
        Checks if the rate is outlier based on post_standard_deviation and post_average_rate
        """
        # About 68% of the data falls within three standard deviations
        # About 95% of the data falls within two standard deviations
        # About 99.7% of the data falls within one standard deviation (we use this)
        standard_deviation_ratio = 1

        # at least 1000 Statistical rates needed to find outlier rates
        min_total_rates_required = 1000

        if not (post_standard_deviation and post_average_rate and post_rates_count):
            post = Post.objects.get(id=self.post_id)
            post_standard_deviation = post.standard_deviation
            post_average_rate = post.normal_average_rate
            post_rates_count = post.rates_count
        if post_rates_count < min_total_rates_required:
            return False
        min_value = post_average_rate - (standard_deviation_ratio * post_standard_deviation)
        max_value = post_average_rate + (standard_deviation_ratio * post_standard_deviation)
        if min_value <= self.score <= max_value:
            return False
        return True

    @staticmethod
    def calculate_weight(
            post_rating_speed_weight,
            user_weight,
            is_outlier

    ):
        """
        calculate the final weight of the rate based on  post_rating_speed_weight, user_weight and is_outlier
        """
        if is_outlier:
            return 0
        rating_speed_weight_ratio = 1
        user_weight_ratio = 2
        weight = (
                (
                        (rating_speed_weight_ratio * post_rating_speed_weight)
                        + (user_weight_ratio * user_weight)
                )
                / (rating_speed_weight_ratio + user_weight_ratio)
        )

        return round(weight, 3)

    def save(self, *args, **kwargs):
        """
        override save method to handle some changes in adding and updating state on instance
        """
        if self._state.adding:
            # update basic statistics of the related post and user in adding state of instance
            User.objects.get(id=self.user_id).increase_rates_count()
            Post.objects.get(id=self.post_id).update_statistics(self.score)
        else:
            # if rate has weight while updating score, rates has affected the average rate of post,
            # so changing the score will change the weighted_total_rates_sum directly with the same weight
            if self.weight:
                pre_rate_score = Rate.objects.get(id=self.id).score
                if self.score != pre_rate_score:
                    Post.objects.filter(id=self.post_id).update(
                        weighted_total_rates_sum=F('weighted_total_rates_sum') - (pre_rate_score * self.weight) + (
                                    self.score * self.weight),
                    )
        super().save(*args, **kwargs)
