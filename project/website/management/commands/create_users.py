# website/management/commands/create_users.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates initial users for all apartments'

    def handle(self, *args, **kwargs):
        floors = ['001', '002', '003', '004'] + [f'{i}01' for i in range(1, 8)] + [f'{i}02' for i in range(1, 8)] + [f'{i}03' for i in range(1, 8)] + [f'{i}04' for i in range(1, 8)]
        
        for floor in floors:
            username = f'121-{floor}'
            email = f'{username}@maurel.com'
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    apartment_number=username,
                    password='torresdelmaurel',
                    email=email  # Set a unique email for each user
                )
                self.stdout.write(self.style.SUCCESS(f'Successfully created user {username} with email {email}'))
            else:
                self.stdout.write(self.style.WARNING(f'User {username} already exists'))