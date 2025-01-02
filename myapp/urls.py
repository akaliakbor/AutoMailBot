from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('show-data/', views.show_data, name='show_data'),
    path('status/', views.email_status, name='email_status'),
    path('terminate/', views.terminate_scheduler_view, name='terminate_scheduler'),
]