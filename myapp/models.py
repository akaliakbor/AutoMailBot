from django.db import models

# Create your models here.
class Emails(models.Model):
    sender_email = models.EmailField()
    receiver_email = models.EmailField()
    email_count = models.IntegerField()

    def __str__(self):
        return self.sender_email