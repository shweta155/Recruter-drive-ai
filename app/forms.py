# app/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.contrib.auth import get_user_model
from .models import User, UserProfile
from .models import Department, Skill
from .models import Section
from .models import QuestionPaper
import re
from django.core.exceptions import ValidationError

User = get_user_model()
from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):
    """
    Custom login form to add specific validation for email and password fields.
    """

    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Enter your email address",
                "autofocus": True,
                "autocomplete": "username",
            }
        ),
    )

    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "••••••••",
                "minlength": "8",
                "maxlength": "64",
                "autocomplete": "current-password",
            }
        ),
    )

    # def clean_username(self):
    #     username = self.cleaned_data.get("username")
    #     if username and not username.strip():
    #         raise ValidationError(
    #             "This field cannot be blank or contain only whitespace.",
    #             code="whitespace_username",
    #         )
    #     return username.strip()
    def clean_username(self):
        username = self.cleaned_data.get("username", "").strip()

        # Find user case-insensitive
        try:
            user = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            raise ValidationError("This email is not registered.", code="invalid")

        # replace with actual stored username casing
        self.cleaned_data["username"] = user.username

        return user.username

    def clean_password(self):
        """
        Adds server-side validation for the password field.
        """
        password = self.cleaned_data.get("password")
        if password and not password.strip():
            raise ValidationError(
                "Password cannot contain only whitespace.", code="whitespace_password"
            )

        password = password.strip()

        if len(password) < 8:
            raise ValidationError(
                "Password must be at least 8 characters long.", code="min_length"
            )
        # ✨ YAHAN BADLAV KIYA GAYA HAI ✨
        if len(password) > 64:
            raise ValidationError(
                "Password is too long. Please use a password with 64 characters or less.",
                code="max_length",
            )

        return password


INPUT_CLASSES = (
    "mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm "
    "placeholder-gray-400 focus:outline-none focus:ring-blue-primary "
    "focus:border-blue-primary sm:text-sm"
)
TEXTAREA_CLASSES = f"{INPUT_CLASSES} resize-y"


# -------------------- USER REGISTRATION FORM --------------------
class UserRegistrationForm(BaseUserCreationForm):
    """
    Handles new user creation with consistent Tailwind styling.
    """

    email = forms.EmailField(
        required=True, help_text="A valid email address is required."
    )
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if field.label:
                placeholder_text = f"Enter your {field.label.lower()}..."
            else:
                placeholder_text = f"Enter {field_name.replace('_', ' ')}..."

            field.widget.attrs.update(
                {"class": INPUT_CLASSES, "placeholder": placeholder_text}
            )

    def clean_email(self):
        """
        Validates that the email is not already registered.
        """
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(username__iexact=email).exists():
            raise forms.ValidationError("Email already registered. Please login.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"].lower()
        if commit:
            user.save()
        return user

    class Meta(BaseUserCreationForm.Meta):
        model = User
        fields = ("email", "first_name", "last_name")


# -------------------- USER PROFILE FORM --------------------
class UserProfileRegistrationForm(forms.ModelForm):
    """
    Handles the user profile fields (phone, address) with same styling.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.label:
                placeholder_text = f"Enter your {field.label.lower()}..."
            else:
                placeholder_text = f"Enter {field_name.replace('_', ' ')}..."

            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update(
                    {
                        "class": TEXTAREA_CLASSES,
                        "rows": "1",
                        "placeholder": placeholder_text,
                    }
                )
            else:
                field.widget.attrs.update(
                    {"class": INPUT_CLASSES, "placeholder": placeholder_text}
                )

    class Meta:
        model = UserProfile
        fields = ("phone_number", "address")


class DepartmentForm(forms.ModelForm):
    sections = forms.ModelMultipleChoiceField(
        queryset=Section.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        error_messages={
            "required": "Please select at least one section for the department."
        },
    )

    class Meta:
        model = Department
        fields = ["name", "sections"]

    def clean_name(self):
        """
        Custom validation to prevent ONLY exact duplicate department names (case-insensitive).
        """
        name = self.cleaned_data.get("name", "").strip()

        # ✨ YEH NAYA AUR BEHTAR LOGIC HAI ✨
        # __iexact ka matlab hai: case-insensitive (chote/bade letters se farak nahi padta) EXACT match.
        query = Department.objects.filter(name__iexact=name)

        # Agar form edit ho raha hai, toh khud ko check na karein
        if self.instance.pk:
            query = query.exclude(pk=self.instance.pk)

        # Agar is naam ka koi department pehle se hai, toh error dein
        if query.exists():
            raise forms.ValidationError(
                "A department with this exact name already exists. Please use a different name."
            )

        return name


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = "__all__"


text_input_class = "w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-theme-primary focus:border-theme-primary"

text_input_class = "w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-theme-primary focus:border-theme-primary"


class QuestionPaperEditForm(forms.ModelForm):
    
    job_title = forms.CharField(
        min_length=3,
        max_length=30,  
        widget=forms.TextInput(attrs={"class": text_input_class}),
    )

    class Meta:
        model = QuestionPaper
        fields = [
            "job_title",
            "title",
            "department_name",
            "duration",
            "min_exp",
            "max_exp",
            "skills_list",
            "cutoff_score",
        ]
        widgets = {
            "job_title": forms.TextInput(attrs={"class": text_input_class}),
            "title": forms.TextInput(attrs={"class": text_input_class}),
            "department_name": forms.TextInput(attrs={"class": text_input_class}),
            "duration": forms.NumberInput(
                attrs={"class": text_input_class, "min": "1"}
            ),
            "min_exp": forms.NumberInput(
                attrs={"class": text_input_class, "id": "min_exp_input", "min": "0"}
            ),
            "max_exp": forms.NumberInput(
                attrs={"class": text_input_class, "id": "max_exp_input", "min": "0"}
            ),
            "skills_list": forms.TextInput(
                attrs={
                    "class": f"{text_input_class} skill-autocomplete-input",  
                    "placeholder": "e.g., Python, Django, JavaScript",
                    "autocomplete": "off",  
                }
            ),
        }

  
    def clean_job_title(self):
        """
        Adds custom validation for the job_title field.
        Ensures the job title is a string with a length between 3 and 30 characters.
        """
        job_title = self.cleaned_data.get("job_title", "").strip()

        if len(job_title) < 3:
            raise forms.ValidationError("Job title must be at least 3 characters long.")

        if len(job_title) > 30:  
            raise forms.ValidationError(
                "Job title cannot be longer than 30 characters."  
            )

        if not re.search(r"[a-zA-Z]", job_title):
            raise forms.ValidationError("Job title must contain letters.")

        return job_title


text_input_class = "w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-theme-primary focus:border-theme-primary"


SKILL_ALIASES = {
    "reactjs": "react",
    "vuejs": "vue",
    "node js": "nodejs",
    "angular js": "angular",
}
SKILL_ALIASES = {
    "reactjs": "react",
    "vuejs": "vue",
    "node js": "nodejs",
    "angular js": "angular",
}


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ["name", "is_active"]

    def clean_name(self):
        """
        Custom validation for the skill name.
        1. Converts the name to lowercase.
        2. Checks for aliases (e.g., reactjs -> react).
        3. Checks for case-insensitive uniqueness.
        """
        name = self.cleaned_data.get("name")
        if name:
            if self.instance and self.instance.name.lower() == name.strip().lower():
                return name  

            cleaned_name = name.strip().lower()

            if cleaned_name in SKILL_ALIASES:
                cleaned_name = SKILL_ALIASES[cleaned_name]

            if Skill.objects.filter(name__iexact=cleaned_name).exists():
                raise forms.ValidationError(
                    "This skill already exists. Please use the existing one."
                )

            return cleaned_name
        return name


text_input_class = "w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-theme-primary focus:border-theme-primary"

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        required=True,
        error_messages={
            "required": "Email address is required.",
            "invalid": "Please enter a valid email address.",
        },
    )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        blocked_domains = ["test.com", "example.com", "mailinator.com", "fake.com"]
        domain = email.split("@")[-1]
        if domain in blocked_domains:
            raise forms.ValidationError(
                "Email domain not allowed. Please use your real email."
            )
        return email


class InviteCandidateForm(forms.Form):
    """
    Form for inviting a candidate via email.
    """

    email = forms.EmailField(
        label="Candidate Email",
        required=True,
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Enter candidate's email address",
                "class": INPUT_CLASSES, 
            }
        ),
        error_messages={
            "required": "The candidate's email address is required.",
            "invalid": "Please enter a valid email address.",
        },
    )

    paper_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        
        return email


class SectionForm(forms.ModelForm):
    """Form to create new sections."""
    class Meta:
        model = Section
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-theme-button",
                "placeholder": "Enter section name",
            })
        }
    
    def clean_name(self):
        """Validate that section name doesn't already exist."""
        name = self.cleaned_data.get("name", "").strip()
        if Section.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError("This section already exists.")
        return name

# app/forms.py

class UserUpdateForm(forms.ModelForm):
    """
    Form to update User model fields only.
    """
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'readonly': 'readonly'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({"class": INPUT_CLASSES})
            
            # Email ko greyed out dikhane ke liye (read-only)
            if field_name == 'email':
                field.widget.attrs.update({'class': INPUT_CLASSES + " bg-gray-100 cursor-not-allowed"})

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]