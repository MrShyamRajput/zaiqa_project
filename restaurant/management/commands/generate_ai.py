from django.core.management.base import BaseCommand
from restaurant.ai import generate_ai_suggestions
class Command(BaseCommand):
    help = "Generate AI suggestions daily"

    def handle(self, *args, **kwargs):
        generate_ai_suggestions()
        self.stdout.write("AI Suggestions Generated")