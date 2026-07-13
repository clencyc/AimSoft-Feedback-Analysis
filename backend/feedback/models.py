from django.db import models

# Create your models here.

# feedback forms
class Customer_feedback(models.Model):
    form_id = models.AutoField(primary_key=True)
    satisfaction_level = models.IntegerField(null=True, blank=True)
    recommend_others = models.IntegerField(null=True, blank=True)

    product_quality = models.IntegerField(null=True, blank=True)
    ease_of_use = models.IntegerField(null=True, blank=True)
    customer_support = models.IntegerField(null=True, blank=True)
    value_for_money = models.IntegerField(null=True, blank=True)
    delivery_speed = models.IntegerField(null=True, blank=True)

    # characters
    product_service = models.CharField(max_length=255, null=True, blank=True)
    product_improvement = models.CharField(max_length=255, null=True, blank=True)
    additional_comments = models.CharField(max_length=255, null=True, blank=True)


    def __str__(self):
        return f"Feedback Form {self.form_id}"