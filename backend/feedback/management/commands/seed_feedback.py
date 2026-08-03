# backend/feedback/management/commands/seed_feedback.py
import random
from django.core.management.base import BaseCommand
from feedback.models import Customer_feedback, Organization

class Command(BaseCommand):
    help = "Seeds the database with various customer feedback records"

    def add_arguments(self, parser):
        # Allows you to specify how many records to create (defaults to 10)
        parser.add_argument(
            '--total',
            type=int,
            default=10,
            help='The number of feedback records to create'
        )

    def handle(self, *args, **options):
        total_records = options['total']
        self.stdout.write(f"Generating {total_records} mock customer feedback entries...")

        # Sample pool data for text fields
        products = ["Premium Plan Subscription", "Mobile App UI", "Cloud Storage Extension", "API Access Key"]
        improvements = ["Faster page loading", "Add a dark mode", "Better documentation", "Simplify checkout process"]
        comments = ["Very satisfied with the service!", "Support took a while to reply.", "Overall great experience.", "Will recommend to colleagues."]

        feedback_instances = []

        for _ in range(total_records):
            # Pick standard 1-5 rating values randomly
            entry = Customer_feedback(
                organization=Organization.objects.order_by('?').first(),  # Random organization
                satisfaction_level=random.randint(1, 5),
                recommend_others=random.randint(1, 5),
                product_quality=random.randint(1, 5),
                ease_of_use=random.randint(1, 5),
                customer_support=random.randint(1, 5),
                value_for_money=random.randint(1, 5),
                delivery_speed=random.randint(1, 5),
                
                # Pick randomized text strings from the pools above
                product_service=random.choice(products),
                product_improvement=random.choice(improvements),
                additional_comments=random.choice(comments)
            )
            feedback_instances.append(entry)

        # Use bulk_create for maximum execution performance
        Customer_feedback.objects.bulk_create(feedback_instances)

        self.stdout.write(self.style.SUCCESS(f"Successfully added {total_records} feedback entries!"))
