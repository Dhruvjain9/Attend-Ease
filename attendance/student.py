from django.db import models

# Create your models here.

from django.db import models

class Student(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    interests = models.TextField(blank=True)

    def __str__(self):
        return self.name
