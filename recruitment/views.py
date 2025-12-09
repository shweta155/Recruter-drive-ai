# recruitment/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, DetailView
from django.views.generic.edit import FormView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin 
from django.contrib.auth.decorators import login_required 
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.db import IntegrityError
from django.contrib import messages
from django.utils.text import slugify 
from .models import JobPost, Candidate, RoundFeedback
from .forms import JobPostForm, RoundFeedbackForm, CandidateApplicationForm 
from user_tests.forms import TestRegistrationForm 
from django.shortcuts import render, redirect, get_object_or_404
from user_tests.models import TestRegistration, QuestionPaper 
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.views.generic import DetailView
import datetime 
from .forms import JobPostForm, JobRoundFormSet # Import FormSet
from .models import JobRound

class JobPostListView(LoginRequiredMixin, ListView):
    model = JobPost
    template_name = 'partials/recruiter/job_list.html'
    context_object_name = 'jobs'
    ordering = ['-created_at']  
    paginate_by = 5
def get_queryset(self):
        
        queryset = super().get_queryset()
        
       
        today = datetime.date.today()
        
        JobPost.objects.filter(
            status='Open', 
            end_date__lt=today
        ).update(status='Closed')
        
        
        return queryset.order_by('-created_at')


class JobPostCreateView(LoginRequiredMixin, CreateView):
    model = JobPost
    form_class = JobPostForm
    template_name = 'partials/recruiter/job_Create.html'    
    success_url = reverse_lazy('job_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['question_papers'] = QuestionPaper.objects.all().order_by('id')
        if self.request.POST:
            context['rounds_formset'] = JobRoundFormSet(self.request.POST)
        else:
            context['rounds_formset'] = JobRoundFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        rounds_formset = context['rounds_formset']

        if form.is_valid() and rounds_formset.is_valid():
            try:
                form.instance.created_by = self.request.user
                
                # Slug Generation Logic
                base_slug = slugify(form.instance.title)
                unique_slug = base_slug
                num = 1
                while JobPost.objects.filter(public_link_slug=unique_slug).exists():
                    unique_slug = f'{base_slug}-{num}'
                    num += 1
                form.instance.public_link_slug = unique_slug 
                
                # 1. Job Post Save करें
                self.object = form.save()
                
                # 2. Rounds Formset Save Logic (AUTO ORDERING)
                # commit=False से ऑब्जेक्ट्स मेमोरी में बनेंगे, DB में नहीं
                rounds = rounds_formset.save(commit=False)
                
                # Loop चलाकर अपने आप order सेट करें (1, 2, 3...)
                for index, round_obj in enumerate(rounds):
                    round_obj.job_post = self.object
                    round_obj.order = index + 1  # यहाँ आटोमेटिक आर्डर सेट हो रहा है
                    round_obj.save()

                # अगर कोई राउंड डिलीट किया गया है तो उसे हटाएं
                for deleted_obj in rounds_formset.deleted_objects:
                    deleted_obj.delete()
                
                # Update total rounds count
                self.object.total_rounds = self.object.rounds.count()
                self.object.save()

                messages.success(self.request, f"Job '{form.instance.title}' created successfully!")
                return redirect(self.success_url)
                
            except Exception as e:
                print(f"❌ Database Error: {e}")
                return self.render_to_response(self.get_context_data(form=form))
        else:
            print("❌ FORM INVALID")
            print("Formset Errors:", rounds_formset.errors) # अब error नहीं आएगा
            return self.render_to_response(self.get_context_data(form=form))

class JobPostDetailView(LoginRequiredMixin, DetailView):
    model = JobPost
    template_name = 'partials/recruiter/job_list.html'
    context_object_name = 'job'
    
    
    def get_object(self, queryset=None):
        job = super().get_object(queryset)
        
        if job.status == 'Open' and job.end_date and job.end_date < datetime.date.today():
            job.status = 'Closed'
            job.save()
            
        return job

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
    
        context['jobs'] = JobPost.objects.all().order_by('-created_at') 
        context['candidate_count'] = context['job'].candidates.count()
        context['application_link'] = self.request.build_absolute_uri(
            reverse('job_application', kwargs={'slug': context['job'].public_link_slug})
        )
        return context


class CandidateListView(LoginRequiredMixin, ListView):
    model = Candidate
    template_name = 'partials/recruiter/candidate_list.html'
    context_object_name = 'candidates'

    def get_queryset(self):
       
        self.job_post = get_object_or_404(JobPost, pk=self.kwargs['job_pk'])
        

        queryset = Candidate.objects.filter(job_post=self.job_post)
        
 
        round_filter = self.request.GET.get('round')
        if round_filter:
           
            valid_rounds = [choice[0] for choice in Candidate.ROUND_CHOICES]
            if round_filter in valid_rounds:
                queryset = queryset.filter(current_round=round_filter)
        
      
        search_query = self.request.GET.get('search')
        if search_query:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(test_registration__name__icontains=search_query) |
                Q(test_registration__email__icontains=search_query)
            )
            
        return queryset.order_by('current_round', '-test_registration__score')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['job'] = self.job_post
        context['round_choices'] = Candidate.ROUND_CHOICES 
        
        context['current_search'] = self.request.GET.get('search', '') 
        return context


@login_required 
def move_candidate_round(request, pk, round_name):
    """Function to manually or programmatically move a candidate to the next round."""
    candidate = get_object_or_404(Candidate, pk=pk)
    
    # Basic security check against invalid round names
    valid_rounds = [choice[0] for choice in Candidate.ROUND_CHOICES]
    if round_name not in valid_rounds:
        messages.error(request, f"Invalid round name: {round_name}")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('job_list')))

    candidate.current_round = round_name
    candidate.is_hired = (round_name == 'Final Offer') # Set hire status if moving to final offer
    candidate.save()
    
    messages.success(request, f"Candidate {candidate.name} moved to **{round_name}**.")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('job_list')))



def job_application_view(request, slug):
    """Public view for candidate to apply for a job."""
    
 
    job_post = get_object_or_404(JobPost, public_link_slug=slug)
    
 
    today = datetime.date.today()

    if job_post.status == 'Open' and job_post.end_date and job_post.end_date < today:
        job_post.status = 'Closed'
        job_post.save()
    if job_post.status == 'Closed':
        return render(request, 'partials/recruiter/job_closed.html', {'job': job_post})

    if request.method == 'POST':
        form = CandidateApplicationForm(request.POST, request.FILES)
        
        # Manually set job_post_pk
        form.data = form.data.copy()
        form.data['job_post_pk'] = job_post.pk
        
        if form.is_valid():
            
            cleaned_data = form.cleaned_data
            email = cleaned_data['email']
            
            try:
                
                if Candidate.objects.filter(job_post=job_post, test_registration__email=email).exists():
                    messages.warning(request, "You have already applied for this job.")
                    return redirect('job_application', slug=slug)

                
                # Step A: Create the TestRegistration object (required by Candidate's FK)
                registration = TestRegistration.objects.create(
                    name=cleaned_data['full_name'],
                    email=email,
                    question_paper=job_post.question_paper if job_post.question_paper else None 
                )
                
                # Step B: Create the Candidate profile, saving ALL the form data.
                candidate = Candidate.objects.create(
                    test_registration=registration,
                    job_post=job_post,
                    current_round='Applied',
                    
                    # Mapping the new fields from the form to the Candidate model:
                    is_experienced=cleaned_data['is_experienced'],
                    mobile=cleaned_data['mobile'],
                    your_skills=cleaned_data.get('your_skills'),
                    total_experience=cleaned_data.get('total_experience'),
                    current_location=cleaned_data.get('current_location'),
                    current_ctc=cleaned_data.get('current_ctc'),
                    current_ctc_rate=cleaned_data.get('current_ctc_rate'),
                    expected_ctc=cleaned_data.get('expected_ctc'),
                    expected_ctc_rate=cleaned_data.get('expected_ctc_rate'),
                    notice_period=cleaned_data.get('notice_period'),
                    heard_about_us=cleaned_data.get('heard_about_us'),
                    cover_letter=cleaned_data.get('cover_letter'),
                    
                    # Handle FileFields (files are in cleaned_data directly if present)
                    cv_or_resume=cleaned_data.get('cv_or_resume'),
                    photo=cleaned_data.get('photo'),
                )
                
                
                messages.success(request, "Application submitted successfully! We will contact you soon.")
                
                if job_post.question_paper:
                     # If a test is linked, redirect to the test start page
                     return redirect('test_start_page', paper_id=job_post.question_paper.id)
                else:
                    # Assuming you have an application_success.html template
                    return render(request, 'partials/public/application_success.html', {'job': job_post, 'candidate': candidate}) 
                
            except IntegrityError as e:
                print(f"Database Error: {e}") 
                messages.error(request, "An unexpected error occurred. Please contact support.")
                if 'registration' in locals():
                    registration.delete()
                return redirect('job_application', slug=slug) 
            except Exception as e:
                print(f"General Error: {e}")
                messages.error(request, "An application error occurred. Please try again.")
                return redirect('job_application', slug=slug) 

    else:
        initial_data = {'job_post_pk': job_post.pk, 'is_experienced': 'fresher'}
        form = CandidateApplicationForm(initial=initial_data)

    return render(request, 'partials/recruiter/job_application.html', {'job': job_post, 'form': form})

class CandidateDetailView(LoginRequiredMixin, DetailView):
    model = Candidate
    template_name = 'partials/recruiter/candidate_detail.html'
    context_object_name = 'candidate'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['job'] = self.object.job_post
        
        try:
            context['feedbacks'] = self.object.feedbacks.all().order_by('-created_at')
        except AttributeError:
            context['feedbacks'] = []
            
        return context


class CandidateKanbanView(LoginRequiredMixin, DetailView):
    model = JobPost
    template_name = 'partials/recruiter/candidate_kanban.html'
    context_object_name = 'job'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job = self.object
        candidates = job.candidates.all()

        kanban_data = []
        for cand in candidates:
            # Color logic
            color = "#5dc3f0" 
            if cand.current_round == 'Rejected': color = "#ef4444"
            elif cand.current_round == 'Final Offer': color = "#22c55e"
            
            kanban_data.append({
                'id': str(cand.id),
                'state': cand.current_round,
                'label': cand.name,
                'tags': f"Score: {cand.test_registration.score or 'N/A'}",
                'hex': color,
                'resourceId': cand.id,
                'detail_url': reverse('candidate_detail', kwargs={'pk': cand.pk}) 
            })

        context['kanban_data'] = json.dumps(kanban_data)
        
        columns = [
            {'text': 'Applied', 'dataField': 'Applied'},
            {'text': 'Written Test', 'dataField': 'Written Test Passed'}, 
            {'text': 'GD Round', 'dataField': 'GD Round'},
            {'text': 'Technical Interview', 'dataField': 'Interview Round'},
            {'text': 'HR Interview', 'dataField': 'HR Round'},
            {'text': 'Final Offer', 'dataField': 'Final Offer'},
            {'text': 'Rejected', 'dataField': 'Rejected'}
        ]
        context['kanban_columns'] = json.dumps(columns)
        return context
# recruitment/views.py

@csrf_exempt 
@login_required
def update_candidate_kanban_status(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            candidate_id = data.get('candidate_id')
            new_status = data.get('new_status')

            if not candidate_id:
                return JsonResponse({'success': False, 'message': "ID Missing"})

            candidate = Candidate.objects.get(pk=candidate_id)
            current_round = candidate.current_round

            # --- 🛑 KANBAN GATEKEEPER LOGIC ---
            
            # Agar same column me drop kiya ya Rejected me dala toh allow karo
            if new_status != current_round and new_status != 'Rejected':
                
                # In rounds me feedback check mat karo
                skip_check_rounds = ['Applied', 'Written Test Passed']
                
                if current_round not in skip_check_rounds:
                    has_feedback = RoundFeedback.objects.filter(
                        candidate=candidate, 
                        round_name=current_round
                    ).exists()

                    if not has_feedback:
                        # Frontend ko error bhejo taaki wo alert dikhaye
                        return JsonResponse({
                            'success': False, 
                            'message': f"Please fill Evaluation Form for {current_round} first!"
                        })
            # ----------------------------------
            
            # Update Round
            candidate.current_round = new_status
            
            if new_status == 'Final Offer':
                candidate.is_hired = True
            elif new_status == 'Rejected':
                candidate.is_hired = False
            
            candidate.save()
            return JsonResponse({'success': True, 'message': f"Moved to {new_status}"})

        except Candidate.DoesNotExist:
             return JsonResponse({'success': False, 'message': "Candidate not found"})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
            
    return JsonResponse({'success': False})


from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db import transaction
from django.contrib import messages
from .models import EvaluationTemplate
from .forms import EvaluationTemplateForm, EvaluationParameterFormSet

class EvaluationTemplateListView(LoginRequiredMixin, ListView):
    model = EvaluationTemplate
    template_name = 'partials/recruiter/evaluation_template_list.html'
    context_object_name = 'templates'

class EvaluationTemplateCreateView(LoginRequiredMixin, CreateView):
    model = EvaluationTemplate
    form_class = EvaluationTemplateForm
    template_name = 'partials/recruiter/evaluation_template_create.html'
    success_url = reverse_lazy('evaluation_template_list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['parameters'] = EvaluationParameterFormSet(self.request.POST)
        else:
            data['parameters'] = EvaluationParameterFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        parameters = context['parameters']
        
        with transaction.atomic():
            form.instance.created_by = self.request.user
            self.object = form.save()
            
            if parameters.is_valid():
                parameters.instance = self.object
                parameters.save()
            else:
                return self.render_to_response(self.get_context_data(form=form))
        
        messages.success(self.request, "Evaluation Template created successfully!")
        return super().form_valid(form)
    model = EvaluationTemplate
    form_class = EvaluationTemplateForm
    template_name = 'partials/recruiter/evaluation_template_create.html'
    success_url = reverse_lazy('evaluation_template_list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['parameters'] = EvaluationParameterFormSet(self.request.POST)
        else:
            data['parameters'] = EvaluationParameterFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        parameters = context['parameters']
        
        with transaction.atomic():
            form.instance.created_by = self.request.user
            self.object = form.save()
            
            if parameters.is_valid():
                parameters.instance = self.object
                parameters.save()
        
        messages.success(self.request, "Evaluation Template created successfully!")
        return super().form_valid(form)



from .models import RoundMaster
from .forms import RoundMasterForm

class RoundMasterListView(LoginRequiredMixin, ListView):
    model = RoundMaster
    template_name = 'partials/recruiter/round_master_list.html'
    context_object_name = 'rounds'

class RoundMasterCreateView(LoginRequiredMixin, CreateView):
    model = RoundMaster
    form_class = RoundMasterForm
    template_name = 'partials/recruiter/round_master_create.html'
    success_url = reverse_lazy('round_master_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, f"Round '{form.instance.name}' created successfully!")
        return super().form_valid(form)


from django.views.generic import UpdateView

class JobPostUpdateView(LoginRequiredMixin, UpdateView):
    model = JobPost
    form_class = JobPostForm
    template_name = 'partials/recruiter/job_edit.html'  
    success_url = reverse_lazy('job_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.POST:
            context['rounds_formset'] = JobRoundFormSet(self.request.POST, instance=self.object)
        else:
            context['rounds_formset'] = JobRoundFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        rounds_formset = context['rounds_formset']

        if form.is_valid() and rounds_formset.is_valid():
            try:
                self.object = form.save()
                
           
                rounds = rounds_formset.save(commit=False)
                
              
                for deleted_obj in rounds_formset.deleted_objects:
                    deleted_obj.delete()

                for index, round_obj in enumerate(rounds):
                    round_obj.job_post = self.object
                    round_obj.order = index + 1
                    round_obj.save()
                
                self.object.total_rounds = self.object.rounds.count()
                self.object.save()

                messages.success(self.request, f"Job '{form.instance.title}' updated successfully!")
                return redirect(self.success_url)
                
            except Exception as e:
                print(f"❌ Database Error: {e}")
                return self.render_to_response(self.get_context_data(form=form))
        else:
            return self.render_to_response(self.get_context_data(form=form))





from django.views.generic import DeleteView


class JobPostDeleteView(LoginRequiredMixin, DeleteView):
    model = JobPost
    success_url = reverse_lazy('job_list')
    
    template_name = 'partials/recruiter/job_confirm_delete.html'



from django.views.decorators.http import require_POST

@login_required
@require_POST
def update_job_status_ajax(request):
    try:
        data = json.loads(request.body)
        job_id = data.get('job_id')
        new_status = data.get('status')

        job = get_object_or_404(JobPost, pk=job_id, created_by=request.user)
        job.status = new_status
        job.save()

        return JsonResponse({'success': True, 'message': f"Status updated to {new_status}"})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)




class FeedbackCreateView(LoginRequiredMixin, CreateView):
    model = RoundFeedback
    form_class = RoundFeedbackForm
    template_name = 'partials/recruiter/feedback_form.html'

    # --- 🛑 YE FUNCTION ADD KAREIN (Fix for ImproperlyConfigured) ---
    def get_success_url(self):
        job_pk = self.object.candidate.job_post.pk
        
      
        next_page = self.request.GET.get('next')
        
        if next_page == 'kanban':
           
            return reverse('candidate_kanban', kwargs={'pk': job_pk})
        
        
        return reverse('candidate_list', kwargs={'job_pk': job_pk})

    def get_initial(self):
        initial = super().get_initial()
        initial['candidate_id'] = self.request.GET.get('candidate_id')
        return initial

    def get_context_data(self, **kwargs):
        """Ye function Template ko data bhejta hai (Header details ke liye)"""
        context = super().get_context_data(**kwargs)
        
        candidate_id = self.request.GET.get('candidate_id') or self.request.POST.get('candidate_id')
        
        if candidate_id:
            candidate = get_object_or_404(Candidate, pk=candidate_id)
            context['candidate'] = candidate
            context['current_round'] = candidate.current_round
        
        return context

    def get_form_kwargs(self):
        """Form ko initialize karte waqt Dynamic Parameters pass karein"""
        kwargs = super().get_form_kwargs()
        
        candidate_id = self.request.GET.get('candidate_id') or self.request.POST.get('candidate_id')
        
        if candidate_id:
            candidate = get_object_or_404(Candidate, pk=candidate_id)
            
           
            current_status = candidate.current_round
           
            
            job_round = JobRound.objects.filter(
                job_post=candidate.job_post,
                round_master__round_type=current_status  
            ).first()
            
        
            
            params = []
            
          
            if job_round and job_round.round_master.evaluation_template:
                print(f"Loading Template: {job_round.round_master.evaluation_template.name} for Round: {current_status}")
                
                params = job_round.round_master.evaluation_template.parameters.all()
            else:
                print(f"No Template found for Round: {current_status}")

            kwargs['evaluation_parameters'] = params
            
        return kwargs

    def form_valid(self, form):
        candidate_id = form.cleaned_data['candidate_id']
        candidate = get_object_or_404(Candidate, pk=candidate_id)

        form.instance.candidate = candidate
        form.instance.interviewer = self.request.user
        form.instance.round_name = candidate.current_round 

        
        total_score = 0
        for field_name, value in form.cleaned_data.items():
            if field_name.startswith('param_'):
                total_score += value
        
        form.instance.score = total_score 
        
        try:
            response = super().form_valid(form)
            
         
            recommendation = form.cleaned_data['recommendation']
            round_names = [c[0] for c in Candidate.ROUND_CHOICES]
            
            current_index = -1
            if candidate.current_round in round_names:
                current_index = round_names.index(candidate.current_round)

            if recommendation == 'Pass':
                if candidate.current_round == 'HR Round':
                    candidate.current_round = 'Final Offer'
                    candidate.is_hired = True
                    messages.success(self.request, "Hired! Candidate moved to Final Offer.")
                elif current_index != -1 and current_index < len(round_names) - 1:
                    next_round = round_names[current_index + 1]
                    if next_round == 'Rejected':
                         next_round = 'Final Offer'
                    candidate.current_round = next_round
                    messages.success(self.request, f"Feedback Saved. Candidate moved to {next_round}.")
            
            elif recommendation == 'Fail':
                candidate.current_round = 'Rejected'
                messages.warning(self.request, "Candidate Rejected.")
            
            candidate.save()
            return response

        except IntegrityError:
             messages.error(self.request, "Feedback already exists for this round.")
             return self.form_invalid(form)

@login_required 
def move_candidate_round(request, pk, round_name):
    """
    Manually move candidate via dropdown.
    RESTRICTION: Cannot move from GD/Interview/HR unless feedback is submitted.
    """
    candidate = get_object_or_404(Candidate, pk=pk)
    current_round = candidate.current_round

    # --- 🛑 GATEKEEPER LOGIC START ---
    
    # In rounds se nikalne ke liye Feedback ki zaroorat nahi hai
    skip_check_rounds = ['Applied', 'Written Test Passed', 'Rejected', 'Final Offer']
    
    # Agar current round skip list mein NAHI hai (Matlab GD, Interview, HR hai)
    if current_round not in skip_check_rounds:
        # Check karein ki kya is round ka feedback database mein hai?
        has_feedback = RoundFeedback.objects.filter(
            candidate=candidate, 
            round_name=current_round
        ).exists()

        if not has_feedback:
            # Agar feedback nahi mila, toh Error dikhao aur wapas bhej do
            messages.error(request, f"⚠️ Cannot move! Please submit Evaluation Form for **{current_round}** first.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('job_list')))
            
    # --- 🛑 GATEKEEPER LOGIC END ---

    # Basic validity check
    valid_rounds = [choice[0] for choice in Candidate.ROUND_CHOICES]
    if round_name not in valid_rounds:
        messages.error(request, f"Invalid round name: {round_name}")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('job_list')))

    # Move Candidate
    candidate.current_round = round_name
    candidate.is_hired = (round_name == 'Final Offer') 
    candidate.save()
    
    messages.success(request, f"Candidate {candidate.name} moved to **{round_name}**.")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('job_list')))