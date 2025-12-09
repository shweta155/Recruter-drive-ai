# user_tests/urls.py

from django.urls import path
from . import views # user_tests/views.py se views import honge
app_name = 'test' 

urlpatterns = [
    # --- USER TEST FLOW ROUTES (MOVED HERE) ---
    path("register/<str:link_id>/", views.user_register_view, name="user_register_link"),
    path("instructions/<str:link_id>/", views.user_instruction_view, name="user_instructions"),
    path("start/<str:link_id>/", views.user_test_view, name="user_test"),
    path("already-submitted/", views.user_already_submitted_view, name="user_already_submitted"),
    path('<str:link_id>/time/', views.get_time_remaining_api, name='get_time_remaining_api'),

]