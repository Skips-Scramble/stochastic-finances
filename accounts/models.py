from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """Custom user class"""

    pass

    def __str__(self):
        return self.email
