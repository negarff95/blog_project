from django.core.cache import cache
from rest_framework import serializers
from .models import Post, Rate


class PostSerializer(serializers.ModelSerializer):
    average_rate = serializers.SerializerMethodField(read_only=True)
    rate_counts = serializers.SerializerMethodField(read_only=True)
    user_rate = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = ['pk', 'title', 'average_rate', 'rate_counts', 'user_rate']

    def get_average_rate(self, obj):
        cache_key = f'AVERAGE_RATE_{obj.id}_POST'
        avg_rate = cache.get(cache_key)  # get cached value
        if avg_rate:
            return avg_rate
        avg_rate = obj.weighted_average_rate
        cache.set(cache_key, avg_rate, 5 * 60)  # cache the value for 5 minutes
        return avg_rate

    def get_rate_counts(self, obj):
        cache_key = f'RATES_COUNT_{obj.id}_POST'
        rates_count = cache.get(cache_key) # get cached value
        if rates_count:
            return rates_count
        rates_count = obj.rates_count
        cache.set(cache_key, rates_count, 5 * 60)  # cache the value for 5 minutes
        return rates_count

    def get_user_rate(self, obj):
        try:
            user = self.context['user']
            rate = Rate.objects.filter(post=obj, user=user)
            score = rate.score
        except Exception:
            return None
        return score


class RateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rate
        fields = ['score', 'post']

    def create(self, validated_data):
        user = self.context['user']
        post = validated_data['post']
        score = validated_data['score']
        rate, created = Rate.objects.update_or_create(
            post=post,
            user=user,
            defaults={'score': score},
        )  # create new rate for given post and user if not exist, else update the score
        cache_count_key = f'RATES_COUNT_{post.id}_POST'
        cache_avg_key = f'AVERAGE_RATE_{post.id}_POST'
        cache.delete(cache_count_key)  # remove post's cached count rate while adding or updating rates
        cache.delete(cache_avg_key)  # remove post's cached average rate while adding or updating rates
        return rate
