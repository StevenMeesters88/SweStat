from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('upload_document/', views.upload_document, name='upload_document'),
    path('configure_dashboard/', views.configure_dashboard, name='configure_dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('return_from_dash/', views.return_from_dash, name='return_from_dash'),
    path('change_layout/<str:graph_no>', views.change_layout, name='change_layout')
]
