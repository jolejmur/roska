from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

class Command(BaseCommand):
    help = 'Deletes and recreates the superuser admin@roska.com.'

    def handle(self, *args, **options):
        User = get_user_model()
        email = 'admin@roska.com'
        password = 'Llave123'

        # Delete the user if it exists
        try:
            user = User.objects.get(email=email)
            user.delete()
            self.stdout.write(self.style.SUCCESS(f'Successfully deleted existing user with email {email}.'))
        except ObjectDoesNotExist:
            self.stdout.write(self.style.NOTICE(f'No existing user with email {email} found. Skipping deletion.'))

        # Create the new superuser
        User.objects.create_superuser(email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f'Successfully created superuser with email {email}.'))
