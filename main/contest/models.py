# contest/models.py
from django.db import models
from django.conf import settings # To link to the User model
from problems.models import Problem # Import the Problem model

class Contest(models.Model):
    name = models.CharField(max_length=255, help_text="Name of the contest")
    problems = models.ManyToManyField('problems.Problem', related_name='contests')
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    isAttempted = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @property
    def is_active(self):
        from django.utils import timezone
        now = timezone.now()
        return self.start_time <= now <= self.end_time

    def is_upcoming(self):
        from django.utils import timezone
        now = timezone.now()
        return now < self.start_time

    def is_past(self):
        from django.utils import timezone
        now = timezone.now()
        return now > self.end_time
        