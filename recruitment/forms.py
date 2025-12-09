# recruitment/forms.py
from django import forms
from .models import JobPost, RoundFeedback
from django.core.exceptions import ValidationError
from .models import JobPost, JobRound, RoundMaster  
from django.core.validators import RegexValidator
INPUT_CLASSES = (
    "mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm "
    "placeholder-gray-400 focus:outline-none focus:ring-blue-primary "
    "focus:border-blue-primary sm:text-sm"
)
TEXTAREA_CLASSES = f"{INPUT_CLASSES} resize-y"

from django import forms
from .models import JobPost, RoundFeedback 
from django.core.exceptions import ValidationError

INPUT_CLASSES = (
    "mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm "
    "placeholder-gray-400 focus:outline-none focus:ring-blue-primary "
    "focus:border-blue-primary sm:text-sm"
)
TEXTAREA_CLASSES = f"{INPUT_CLASSES} resize-y"


from django import forms
from .models import JobPost, RoundFeedback
from django.core.exceptions import ValidationError

INPUT_CLASSES = (
    "mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm "
    "placeholder-gray-400 focus:outline-none focus:ring-blue-primary "
    "focus:border-blue-primary sm:text-sm"
)
TEXTAREA_CLASSES = f"{INPUT_CLASSES} resize-y"


class JobPostForm(forms.ModelForm):
    class Meta:
        model = JobPost
        fields = [
        
            'title', 'department', 'location', 'job_type',
            
        
            'experience_min', 'experience_max', 'skills_required', 'positions_available',
            
           
            # 'total_rounds',
            'pay_scale', 'end_date',
            
            'description', 'question_paper', 'status', 
           
        ]
        widgets = {
            # Job Details
            'title': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Job Title (e.g., Senior Django Developer)'}),
            'department': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Department (e.g., Engineering, Sales)'}),
            'location': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'City, State or Remote'}),
            'job_type': forms.Select(attrs={'class': INPUT_CLASSES}),
            
            # Requirements
            'experience_min': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Experience Min (Years)', 'min': 0}),
            'experience_max': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Experience Max (Years)', 'min': 0}),
            'skills_required': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Python, Django, React (comma separated)'}), 
            'positions_available': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Number of Openings', 'min': 1}),

           
            'pay_scale': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'e.g., 8LPA - 12LPA or Negotiable'}),
            'end_date': forms.DateInput(attrs={'class': INPUT_CLASSES, 'type': 'date'}),
            
            
            'description': forms.Textarea(attrs={'class': TEXTAREA_CLASSES, 'rows': 4, 'placeholder': 'Detailed Job Description and Responsibilities'}),
        
            'status': forms.Select(attrs={'class': INPUT_CLASSES}),
        }
        
    def clean_experience_max(self):
        min_exp = self.cleaned_data.get('experience_min')
        max_exp = self.cleaned_data.get('experience_max')
        if max_exp is not None and min_exp is not None and max_exp < min_exp:
            raise ValidationError("Maximum experience cannot be less than Minimum experience.")
        return max_exp



class RoundFeedbackForm(forms.ModelForm):

    candidate_id = forms.IntegerField(widget=forms.HiddenInput())

    class Meta:
        model = RoundFeedback
      
        fields = ['score', 'comments', 'recommendation']
        widgets = {
            'score': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'min': 0, 'max': 10, 'placeholder': 'Score (0-10)'}),
            'comments': forms.Textarea(attrs={'class': TEXTAREA_CLASSES, 'rows': 3, 'placeholder': 'Detailed Feedback/Notes'}),
            'recommendation': forms.RadioSelect(choices=RoundFeedback.RECOMMENDATION_CHOICES),
        }



class CandidateApplicationForm(forms.Form):
    """
    Public form for a candidate to apply directly to a job post.
    Fields match the provided image with Fresher/Experienced selection.
    """
    EXPERIENCE_CHOICES = [
        ('fresher', 'Fresher'),
        ('experienced', 'Experienced'),
    ]
    # 2. Dropdown ke liye choices define karein
    SOURCE_CHOICES = [
        ('', 'Select an option'), # Default empty
        ('linkedin', 'LinkedIn'),
        ('naukri', 'Naukri.com'),
        ('website', 'Company Website'),
        ('referral', 'Friend/Referral'),
        ('social', 'Social Media'),
        ('other', 'Other'),
    ]
    # 📌 Experience Status
    is_experienced = forms.ChoiceField(
        choices=EXPERIENCE_CHOICES,
        widget=forms.Select(attrs={'class': INPUT_CLASSES})
    )
    
    # 📌 Personal Information Fields
    full_name = forms.CharField(
        max_length=255, 
        widget=forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Full Name *'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Email *'})
    )
    mobile = forms.CharField(
        max_length=11, # Database me 15 hai, par form me hum 11 allow karenge
        min_length=11,
        validators=[
            RegexValidator(
                regex=r'^\d{11}$', 
                message='Mobile number must be exactly 11 digits.', 
                code='invalid_mobile'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': INPUT_CLASSES, 
            'placeholder': 'Mobile (11 Digits) *',
            'type': 'tel',  # Mobile keypad numeric open hoga
            'pattern': '[0-9]{11}', # HTML5 validation
            'maxlength': '11', # User 11 se zyada type hi nahi kar payega
            # Ye Javascript user ko sirf number type karne dega:
            'oninput': "this.value = this.value.replace(/[^0-9]/g, '')" 
        })
    )
    
    # 📌 Skills & Experience (Conditional Fields)
    your_skills = forms.CharField(max_length=500, required=False, widget=forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Your Skills'}))
    total_experience = forms.IntegerField(min_value=0, required=False, widget=forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Total Experience'}))
    current_location = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Current Location'}))
    
    # 📌 Compensation & Notice (Conditional Fields)
    current_ctc = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Current CTC ₹'}))
    current_ctc_rate = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Current CTC Rate'}))
    expected_ctc = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Expected CTC ₹'}))
    expected_ctc_rate = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Expected CTC Rate'}))
    notice_period = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Notice Period'}))
    
    # 📌 Source
    # 4. Heard About Us - Ab Dropdown ban gaya hai
    heard_about_us = forms.ChoiceField(
        choices=SOURCE_CHOICES,
        required=False, 
        widget=forms.Select(attrs={'class': INPUT_CLASSES})
    )
    # 📌 File Uploads (Confirmed Optional: required=False)
    cv_or_resume = forms.FileField(
        required=False, 
        widget=forms.ClearableFileInput(attrs={'class': 'hidden', 'id': 'cv_upload'})
    )
    photo = forms.FileField(
        required=False, 
        widget=forms.ClearableFileInput(attrs={'class': 'hidden', 'id': 'photo_upload'})
    )
    
    # 📌 Cover Letter
    cover_letter = forms.CharField(
        widget=forms.Textarea(attrs={'class': TEXTAREA_CLASSES, 'rows': 5, 'placeholder': 'Write a brief cover letter...'}), 
        required=False
    )
    
    job_post_pk = forms.IntegerField(widget=forms.HiddenInput())


class CandidateApplicationForm(forms.Form):
    """
    Public form for a candidate to apply directly to a job post.
    Fields match the provided image with Fresher/Experienced selection.
    """
    EXPERIENCE_CHOICES = [
        ('fresher', 'Fresher'),
        ('experienced', 'Experienced'),
    ]
    # 2. Dropdown ke liye choices define karein
    SOURCE_CHOICES = [
        ('', 'Select an option'), # Default empty
        ('linkedin', 'LinkedIn'),
        ('naukri', 'Naukri.com'),
        ('website', 'Company Website'),
        ('referral', 'Friend/Referral'),
        ('social', 'Social Media'),
        ('other', 'Other'),
    ]
    # 📌 Experience Status
    is_experienced = forms.ChoiceField(
        choices=EXPERIENCE_CHOICES,
        widget=forms.Select(attrs={'class': INPUT_CLASSES})
    )
    
    # 📌 Personal Information Fields
    full_name = forms.CharField(
        max_length=255, 
        widget=forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Full Name *'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Email *'})
    )
    mobile = forms.CharField(
        max_length=11, # Database me 15 hai, par form me hum 11 allow karenge
        min_length=11,
        validators=[
            RegexValidator(
                regex=r'^\d{11}$', 
                message='Mobile number must be exactly 11 digits.', 
                code='invalid_mobile'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': INPUT_CLASSES, 
            'placeholder': 'Mobile (11 Digits) *',
            'type': 'tel',  # Mobile keypad numeric open hoga
            'pattern': '[0-9]{11}', # HTML5 validation
            'maxlength': '11', # User 11 se zyada type hi nahi kar payega
            # Ye Javascript user ko sirf number type karne dega:
            'oninput': "this.value = this.value.replace(/[^0-9]/g, '')" 
        })
    )
    
    # 📌 Skills & Experience (Conditional Fields)
    your_skills = forms.CharField(max_length=500, required=False, widget=forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Your Skills'}))
    total_experience = forms.IntegerField(min_value=0, required=False, widget=forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Total Experience'}))
    current_location = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Current Location'}))
    
    # 📌 Compensation & Notice (Conditional Fields)
    current_ctc = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Current CTC ₹'}))
    current_ctc_rate = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Current CTC Rate'}))
    expected_ctc = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Expected CTC ₹'}))
    expected_ctc_rate = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Expected CTC Rate'}))
    notice_period = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Notice Period'}))
    
    # 📌 Source
    # 4. Heard About Us - Ab Dropdown ban gaya hai
    heard_about_us = forms.ChoiceField(
        choices=SOURCE_CHOICES,
        required=False, 
        widget=forms.Select(attrs={'class': INPUT_CLASSES})
    )
    # 📌 File Uploads (Confirmed Optional: required=False)
    cv_or_resume = forms.FileField(
        required=False, 
        widget=forms.ClearableFileInput(attrs={'class': 'hidden', 'id': 'cv_upload'})
    )
    photo = forms.FileField(
        required=False, 
        widget=forms.ClearableFileInput(attrs={'class': 'hidden', 'id': 'photo_upload'})
    )
    
    # 📌 Cover Letter
    cover_letter = forms.CharField(
        widget=forms.Textarea(attrs={'class': TEXTAREA_CLASSES, 'rows': 5, 'placeholder': 'Write a brief cover letter...'}), 
        required=False
    )
    
    job_post_pk = forms.IntegerField(widget=forms.HiddenInput())
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        if email:
            # Email ko lowercase karein taaki Case Sensitive issue na ho (User@Gmail.com bhi chalega)
            email_check = email.lower()
            
            # Check karein agar @gmail.com ya .in se end ho raha hai
            if not (email_check.endswith('@gmail.com') or email_check.endswith('.in')):
                raise ValidationError("Only Gmail (@gmail.com) or .in domains are allowed.")
        
        return email


# recruitment/forms.py

from django import forms
from django.forms import inlineformset_factory
from .models import EvaluationTemplate, EvaluationParameter
from django import forms
from django.forms import inlineformset_factory
from .models import EvaluationTemplate, EvaluationParameter

from django.core.exceptions import ValidationError
from .models import EvaluationTemplate, EvaluationParameter

class EvaluationTemplateForm(forms.ModelForm):
    class Meta:
        model = EvaluationTemplate
        fields = ['name', 'cutoff_score']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full border p-2 rounded', 
                'placeholder': 'Enter Template Name'
            }),
            'cutoff_score': forms.NumberInput(attrs={
                'class': 'w-full border p-2 rounded',
                'min': '0',    # HTML Limit
                'max': '100',  # HTML Limit
                'step': '1'
            }),
        }

    # Server-Side Validation (Security ke liye)
    def clean_cutoff_score(self):
        score = self.cleaned_data.get('cutoff_score')
        if score is not None:
            if score < 0:
                raise ValidationError("Cutoff score cannot be less than 0.")
            if score > 100:
                raise ValidationError("Cutoff score cannot be greater than 100.")
        return score


class EvaluationParameterForm(forms.ModelForm):
    class Meta:
        model = EvaluationParameter
        fields = ['name', 'weight']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full border p-2 rounded', 
                'placeholder': 'Parameter (e.g. Code Quality)'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'w-20 border p-2 rounded', 
                'placeholder': 'Max',
                'min': '0',   # HTML Limit
                'max': '10',  # HTML Limit
                'step': '1'
            }),
        }

    # Server-Side Validation (Security ke liye)
    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        if weight is not None:
            if weight < 0:
                raise ValidationError("Weight cannot be negative.")
            if weight > 10:
                raise ValidationError("Weight cannot be more than 10.")
        return weight

EvaluationParameterFormSet = inlineformset_factory(
    EvaluationTemplate,
    EvaluationParameter,
    form=EvaluationParameterForm,
    extra=1,
    can_delete=True
)
from .models import RoundMaster # Ensure RoundMaster is imported

class RoundMasterForm(forms.ModelForm):
    class Meta:
        model = RoundMaster
        fields = ['name', 'round_type', 'evaluation_template']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Round Name (e.g. Initial Screening)'}),
            'round_type': forms.Select(attrs={'class': INPUT_CLASSES}),
            'evaluation_template': forms.Select(attrs={'class': INPUT_CLASSES}),
        }


class JobRoundForm(forms.ModelForm):
    class Meta:
        model = JobRound
        fields = ['round_master']
        widgets = {
            'round_master': forms.Select(attrs={
                'class': 'block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'order': forms.HiddenInput()
        }

JobRoundFormSet = inlineformset_factory(
    JobPost,
    JobRound,
    form=JobRoundForm,
    extra=1,      # Default 1 empty row dikhega
    can_delete=True
)



# recruitment/forms.py

class RoundFeedbackForm(forms.ModelForm):
    candidate_id = forms.IntegerField(widget=forms.HiddenInput())

    class Meta:
        model = RoundFeedback
        # Score hum calculate karenge, isliye fields se hata diya
        fields = ['comments', 'recommendation'] 
        widgets = {
            'comments': forms.Textarea(attrs={'class': TEXTAREA_CLASSES, 'rows': 3, 'placeholder': 'Detailed Feedback/Notes'}),
            'recommendation': forms.RadioSelect(choices=RoundFeedback.RECOMMENDATION_CHOICES),
        }

    def __init__(self, *args, **kwargs):
        # View se parameters receive karein
        self.evaluation_parameters = kwargs.pop('evaluation_parameters', None)
        super().__init__(*args, **kwargs)

        # Dynamic Fields generate karein
        if self.evaluation_parameters:
            for param in self.evaluation_parameters:
                field_name = f"param_{param.id}"
                self.fields[field_name] = forms.IntegerField(
                    label=param.name,
                    min_value=0,
                    max_value=param.weight,
                    widget=forms.NumberInput(attrs={
                        'class': INPUT_CLASSES, 
                        'placeholder': f'Max {param.weight}'
                    }),
                    help_text=f"Weightage: {param.weight}"
                )