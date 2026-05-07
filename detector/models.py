from django.db import models
from django.contrib.auth.models import User


class ScanHistory(models.Model):

    TYPE_CHOICES = (
        ('text', 'Text'),
        ('link', 'Link'),
    )

    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    scan_type  = models.CharField(max_length=10, choices=TYPE_CHOICES)
    input_data = models.TextField()
    risk_score = models.IntegerField()
    label      = models.CharField(max_length=20)
    explanation = models.TextField(blank=True, default="")  # blank=True — AI may fail
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']   # newest first by default

    def __str__(self):
        return f"{self.user.username} - {self.scan_type} - {self.label}"