from django.db import models
from django.contrib.auth.models import User
import uuid


class Profile(models.Model):
    # extending user and connecting "Profile" and "User" models
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True,
                          primary_key=True, editable=False)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    profile_img = models.ImageField(null=True, blank=True,
                                    upload_to='profiles/')
    bio = models.TextField(null=True, blank=True)
    hobbies = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.first_name + " " + self.last_name
