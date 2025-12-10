# recruitment/urls.py
from django.urls import path
from . import views
from django.urls import path
from .views import (
    JobPostListView, 
    JobPostCreateView, 
    JobPostDetailView, 
    CandidateListView, 
    move_candidate_round, 
    FeedbackCreateView, 
    job_application_view,
    CandidateKanbanView, 
    update_candidate_kanban_status,
    CandidateDetailView,
    EvaluationTemplateListView,
    EvaluationTemplateCreateView,
    RoundMasterListView,
    RoundMasterCreateView,
    BatchGDEvaluationView
)


urlpatterns = [
 
    path('jobs/', views.JobPostListView.as_view(), name='job_list'),
    path('jobs/create/', views.JobPostCreateView.as_view(), name='job_create'),
    path('jobs/<int:pk>/', views.JobPostDetailView.as_view(), name='job_detail'),
    path('jobs/<int:job_pk>/candidates/', views.CandidateListView.as_view(), name='candidate_list'),
    path('candidate/<int:pk>/move_to/<str:round_name>/', views.move_candidate_round, name='candidate_move_round'),
    path('candidate/<int:pk>/feedback/submit/', views.FeedbackCreateView.as_view(), name='submit_feedback'),
    path('apply/<slug:slug>/', views.job_application_view, name='job_application'),   
    path('jobs/<int:pk>/edit/', views.JobPostUpdateView.as_view(), name='job_edit'), # यह लाइन जोड़ें 
    path('candidate/<int:pk>/feedback/submit/', views.FeedbackCreateView.as_view(), name='submit_feedback'),
    path('job/<int:pk>/kanban/', CandidateKanbanView.as_view(), name='candidate_kanban'),
    path('api/update-kanban-status/', update_candidate_kanban_status, name='update_candidate_kanban_status'),
    path('candidate/<int:pk>/details/', CandidateDetailView.as_view(), name='candidate_detail'),
    path('evaluations/', EvaluationTemplateListView.as_view(), name='evaluation_template_list'),

    path('evaluations/create/', EvaluationTemplateCreateView.as_view(), name='evaluation_template_create'),
    path('rounds/', RoundMasterListView.as_view(), name='round_master_list'),
    path('rounds/create/', RoundMasterCreateView.as_view(), name='round_master_create'),
    path('jobs/<int:pk>/delete/', views.JobPostDeleteView.as_view(), name='job_delete'),
    path('api/update-job-status/', views.update_job_status_ajax, name='update_job_status_ajax'),
    path('job/<int:job_pk>/gd-evaluation/', BatchGDEvaluationView.as_view(), name='gd_batch_evaluation'),
    
]
