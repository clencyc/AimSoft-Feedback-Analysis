# Migration: add rating_dimensions to FeedbackLink and new fields to Customer_feedback
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0003_add_initial_organizations'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedbacklink',
            name='rating_dimensions',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='customer_feedback',
            name='csat_score',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customer_feedback',
            name='nps_score',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customer_feedback',
            name='dimension_ratings',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customer_feedback',
            name='like_most',
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='customer_feedback',
            name='improve',
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='customer_feedback',
            name='additional_comments',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
