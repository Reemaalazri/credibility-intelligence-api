from django.db import models

# Create models
class Claim(models.Model):
    liar_id = models.CharField(max_length=50)
    label = models.CharField(max_length=20)
    statement = models.TextField()
    speaker = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.statement[:50]
