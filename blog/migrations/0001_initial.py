# Generated by Django 5.0.6 on 2024-06-07 17:53

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('title', models.CharField(max_length=100)),
                ('content', models.TextField()),
                ('weighted_total_rates_sum', models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('weighted_rates_count', models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('rates_count', models.PositiveIntegerField(default=0)),
                ('total_rates_sum', models.PositiveIntegerField(default=0)),
                ('total_rates_sum_squared', models.PositiveIntegerField(default=0)),
                ('average_rating_speed', models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Rate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('score', models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(5)])),
                ('weight', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('is_outlier', models.BooleanField(default=False)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rates', to='blog.post')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rates', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'indexes': [models.Index(fields=['post'], name='blog_rate_post_id_b111ce_idx'), models.Index(fields=['user'], name='blog_rate_user_id_45e987_idx')],
                'unique_together': {('post', 'user')},
            },
        ),
    ]
