from django.db import models

# Create your models here.
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
    isSolved = models.BooleanField(default=False)
    topic = models.CharField(max_length=50)
    constraints = models.TextField()

    def __str__(self):
        return f"{self.title}"
