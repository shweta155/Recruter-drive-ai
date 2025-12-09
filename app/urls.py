# app/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.user_login, name="login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path(
        "api/paper/<int:paper_id>/deactivate/",
        views.deactivate_paper,
        name="deactivate_paper",
    ),
    path("logout/", views.user_logout, name="logout"),
    path("register/", views.user_register, name="register"),
    path(
        "password_reset/",
        views.password_reset_request, 
        name="password_reset",
    ),
    
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("generate/", views.generate_questions, name="generate_questions"),
    path("home/", views.home, name="home"),
    path("save-paper/", views.save_paper, name="save_paper"),
    path("papers/", views.list_papers, name="list_papers"),
    path("departments/create/", views.department_create_view, name="department_create"),
    path(
        "departments/<int:department_id>/sections/",
        views.get_sections_by_department,
        name="get_sections_by_department",
    ),
    path("api/skills/", views.get_skills_json, name="get_skills_json"),
    path("skills/", views.skill_list_view, name="skill_list"),
    path("skills/create/", views.skill_create_view, name="skill_create"),
    path("skills/update/<int:pk>/", views.skill_update_view, name="skill_update"),
    path("skills/delete/<int:pk>/", views.skill_delete_view, name="skill_delete"),
    path("paper/<int:paper_id>/", views.paper_detail_view, name="paper_detail"),
    path("paper/<int:paper_id>/edit/", views.paper_edit_view, name="paper_edit"),
    path("paper/take/<int:paper_id>/", views.take_paper, name="take_paper"),
    path(
        "api/paper/<int:paper_id>/toggle-public/",
        views.toggle_paper_public_status,
        name="toggle_paper_public_status",
    ),
    path(
        "paper/<int:paper_id>/partial-update/",
        views.partial_update_view,
        name="partial_update_paper",
    ),
    path("users/", views.user_list, name="user_list"),
    path("users/<int:user_id>/", views.user_detail, name="user_detail"),
    path("users/delete/<int:user_id>/", views.delete_user, name="delete_user"),
    path("profile/<int:pk>/", views.user_profile_view, name="user_profile"),
    path("test-report/<int:registration_id>/", views.test_result, name="test_report"),
    path("regenerate-question/", views.regenerate_question, name="regenerate_question"),
    path(
        "paper/<int:paper_id>/export-participants/",
        views.export_participants_csv,
        name="export_participants_csv",
    ),
    path("submit-test/<int:registration_id>/", views.submit_test, name="submit_test"),
    path(
        "registration/<int:registration_id>/toggle-shortlist/",
        views.toggle_shortlist,
        name="toggle_shortlist",
    ),
    path(
        "invite-candidate/", views.invite_candidate, name="invite_candidate"
    ), 
    path(
    "sections/create/",
    views.create_section_ajax,
    name="create_section_ajax"
),
path('api/skills/search/', views.search_skills_with_suggestions, name='search_skills_suggestions'),
    path('ajax/upload_image/', views.upload_image_ajax, name='upload_image_ajax'),
    path('profile/<int:pk>/edit/', views.edit_user_profile, name='edit_user_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
]
