from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Creates two users and prints their usernames and passwords"

    def handle(self, *args, **kwargs):

        user1 = User.objects.create_user(username="user1", password="Osama1122334455!")

        self.stdout.write(
            f"Created user1 with username: {user1.username}, password: {user1.password}"
        )

        # Create the second user
        user2 = User.objects.create_user(username="user2", password="Osama1122334455!")
        self.stdout.write(
            f"Created user2 with username: {user2.username}, password: {user2.password}"
        )
