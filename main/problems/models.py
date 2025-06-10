from django.db import models
from django.contrib.auth.models import User

class Problem(models.Model):
    DIFFICULTY = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]

    title = models.CharField(max_length=50)
    description = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY)
    input_testcase = models.TextField()
    output_testcase = models.TextField()
    testcase_explanation = models.TextField()
    topic = models.CharField(max_length=50)
    constraints = models.TextField()

    # REMOVE these two lines:
    # isSolved = models.BooleanField(default=False)
    # isSaved = models.BooleanField(default=False)

    # ADD these two lines to track user-specific status:
    solved_by = models.ManyToManyField(User, related_name='solved_problems', blank=True)
    saved_by = models.ManyToManyField(User, related_name='saved_problems', blank=True)

    def __str__(self):
        return f"{self.title}"

    # ADD these helper methods for checking user-specific status in views/templates:
    def get_is_solved_for_user(self, user):
        """Checks if this problem is solved by the given user."""
        if user.is_authenticated:
            return self.solved_by.filter(id=user.id).exists()
        return False

    def get_is_saved_for_user(self, user):
        """Checks if this problem is saved by the given user."""
        if user.is_authenticated:
            return self.saved_by.filter(id=user.id).exists()
        return False
