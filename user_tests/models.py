# user_tests/models.py (THE FINAL VERSION)

from django.db import models
from django.utils import timezone
from app.models import QuestionPaper ,Question


# ----------------------------------------------------------------------
# --- MODEL FOR CANDIDATE REGISTRATION AND REPETITION CHECK ---
# ----------------------------------------------------------------------

class TestRegistration(models.Model):
    """
    Stores one unique attempt (registration) by an email for a specific Question Paper.
    This model has been MOVED from the 'app' module.
    """
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)
    is_shortlisted = models.BooleanField(default=False)

    question_paper = models.ForeignKey(
        QuestionPaper,
        on_delete=models.CASCADE,
        related_name="registrations"
    )

    start_time = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

    class Meta:
        # **THE FIX:** Use the old table name to match the existing data
        db_table = 'app_testregistration'
        
        # **CORE CONSTRAINT:** Ensures same email cannot be used for the same paper twice.
        unique_together = ('email', 'question_paper')

    def __str__(self):
        return f"{self.email} registered for {self.question_paper.title}"

class UserResponse(models.Model):
    """
    Stores the user's answer for a specific question during a test attempt.
    """
    # FK to TestRegistration (Pura test attempt)
    registration = models.ForeignKey(
        TestRegistration, 
        on_delete=models.CASCADE, 
        related_name="responses"
    )
    
    # FK to Question (Kaunsa question tha) - Yeh Question model 'app' se aayega
    question = models.ForeignKey(
        Question, 
        on_delete=models.CASCADE, 
        related_name="user_responses"
    )
    
    # User ne kya answer diya (MCQ ho ya subjective)
    user_answer = models.TextField(blank=True, null=True)
    is_correct = models.BooleanField(null=True, blank=True)
    class Meta:
        # Ek user ek test mein ek question ka sirf ek hi answer de sakta hai
        unique_together = ('registration', 'question')
        # DB Table ka naam default 'user_tests_userresponse' hoga
        
    def __str__(self):
        return f"Response for Q{self.question.id} by {self.registration.name}"