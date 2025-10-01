from django.urls import path
from accounts import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # Gestion des élèves
    path('students/', views.student_list, name='student_list'),
    path('students/<int:pk>/', views.student_detail, name='student_detail'),
    path('students/create/', views.student_create, name='student_create'),
    path('students/<int:pk>/edit/', views.student_edit, name='student_edit'),
    path('students/<int:pk>/archive/', views.student_archive, name='student_archive'),
    
    # Gestion des instructeurs
    path('instructors/', views.instructor_list, name='instructor_list'),
    path('instructors/<int:pk>/', views.instructor_detail, name='instructor_detail'),
    path('instructors/create/', views.instructor_create, name='instructor_create'),
    path('instructors/<int:pk>/edit/', views.instructor_edit, name='instructor_edit'),
    path('instructors/<int:pk>/archive/', views.instructor_archive, name='instructor_archive'),
]