# app/models.py

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db import models
import re

User = get_user_model()


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile for {self.user.username}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Naye User create hone par turant UserProfile banao."""
    if created:
        UserProfile.objects.create(user=instance)

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def pretty_name(self):
        """
        Returns a nicely formatted name for the UI.
        """

        if self.name == "nodejs":
            return "Node.js"
        if self.name == "javascript":
            return "JavaScript"

        return self.name.title()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]

class Section(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=100, default="")
    sections = models.ManyToManyField(Section)

    def __str__(self):
        return self.name


class QuestionPaper(models.Model):
    """
    Represents a complete, saved question paper.
    """

    cutoff_score = models.PositiveIntegerField(
        default=20, help_text="Minimum percentage to pass (e.g., 70)"
    )
    title = models.CharField(max_length=255)
    job_title = models.CharField(max_length=200)
    department_name = models.CharField(max_length=100, default="Unassigned")
    min_exp = models.PositiveIntegerField()
    max_exp = models.PositiveIntegerField()
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    skills_list = models.TextField(
        help_text="Comma-separated list of skills", default=""
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="question_papers",
        null=True,
    )
    total_questions = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    is_active = models.BooleanField(default=False)
    is_public_active = models.BooleanField(null=True, blank=True)
    is_private_link_active = models.BooleanField(default=False) # <--- ADD default=False
    def __str__(self):
        return f"{self.title} for {self.job_title}"


class PaperSection(models.Model):
    """
    Represents a single section within a QuestionPaper.
    """

    question_paper = models.ForeignKey(
        QuestionPaper, on_delete=models.CASCADE, related_name="paper_sections"
    )
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)
    weightage = models.PositiveIntegerField(
        default=0, help_text="Weightage in percentage for this section"
    )

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Section '{self.title}' of paper '{self.question_paper.title}' (Weightage: {self.weightage}%)"
    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Section '{self.title}' of paper '{self.question_paper.title}' (Weightage: {self.weightage}%)"

class Question(models.Model):
    """
    Represents a single question within a PaperSection.
    """

    class QuestionType(models.TextChoices):
        MCQ = "MCQ", "Multiple Choice"
        SA = "SA", "Short Answer"
        CODE = "CODE", "Coding"

    section = models.ForeignKey(
        PaperSection, on_delete=models.CASCADE, related_name="questions"
    )
    text = models.TextField()
    answer = models.TextField()
    options = models.JSONField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)

    question_type = models.CharField(
        max_length=15,
        choices=QuestionType.choices,
    )

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Q: {self.text[:50]}..."


class TestRegistration(models.Model):
    email = models.EmailField(max_length=255)
    phone_number = models.CharField(max_length=15)
    address = models.TextField(null=True, blank=True)
    start_time = models.DateTimeField()
    is_completed = models.BooleanField(default=False)
    question_paper = models.ForeignKey(QuestionPaper, on_delete=models.CASCADE)
    score = models.FloatField(null=True, blank=True)
    is_shortlisted = models.BooleanField(default=False)

    class Meta:
        db_table = "app_testregistration"
        managed = False

    def __str__(self):
        return f"{self.email} - Paper ID: {self.question_paper.id}"

class UserResponse(models.Model):
    user_answer = models.TextField()
    question = models.ForeignKey(Question, on_delete=models.DO_NOTHING)
    registration = models.ForeignKey(TestRegistration, on_delete=models.DO_NOTHING)
    is_correct = models.BooleanField(null=True, blank=True)
    class Meta:
        db_table = "user_tests_userresponse"
        managed = False

    def __str__(self):
        return f"Response for Q:{self.question.id} by Reg:{self.registration.id}"
