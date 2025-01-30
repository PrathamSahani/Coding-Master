from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from django.db import models

class CustomAdmin(models.Model):
    username = models.CharField(max_length=150, unique=True, default="admin")
    password = models.CharField(max_length=150, default="admin123")  

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Custom Admin"
        verbose_name_plural = "Custom Admins"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pics/', default='default.jpg')

    def __str__(self):
        return self.user.username

class Contest(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    base_code = models.TextField()
    start_date = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)  # Track creator

    def __str__(self):
        return self.title

class TestCase(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='test_cases', null=True)
    input_data = models.TextField()
    expected_output = models.TextField()

    def __str__(self):
        return f"TestCase for {self.contest.title}"

class Submission(models.Model):
    STATUS_CHOICES = (
        ('pass', 'Pass'),
        ('fail', 'Fail'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    code = models.TextField()
    language = models.CharField(max_length=10)
    time_taken = models.FloatField(null=True, blank=True)
    test_case_result = models.CharField(max_length=10, choices=STATUS_CHOICES)
    ranking = models.IntegerField(null=True, blank=True)
    submission_time = models.DateTimeField(auto_now_add=True)
    is_submit = models.BooleanField(default=False)  

    def __str__(self):
        return f"{self.user.username} - {self.contest.title}"

from django.db import models
from django.contrib.auth.models import User

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.created_at}"


class Question(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    base_code = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='easy')
    problem_tag = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title


class TestCase_Question(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='test_cases', null=True)
    input_data = models.TextField()
    expected_output = models.TextField()

    def __str__(self):
        return f"TestCase_Question for {self.question.title}"


class Dashboard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    problem_title = models.CharField(max_length=255)
    language = models.CharField(max_length=20)
    code = models.TextField()
    status = models.CharField(max_length=20)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.problem_title}"

from django.db import models

class CodeSubmission(models.Model):
    LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('java', 'Java'),
        ('cpp', 'C++'),
    ]
    
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES)
    code = models.TextField()
    result = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)



