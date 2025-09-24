#attendance/urls.py


from django.urls import path, include
from . import views  # Use relative import for views within attendance app
from .views import generate_qr_code
from .views import validate_qr_scan

app_name = 'attendance'

urlpatterns = [
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('classschedule/<int:classschedule_id>/attendance/', views.mark_attendance, name='mark_attendance'),
    path('classschedule/<int:classschedule_id>/attendance/<str:attendance_date>/', views.mark_attendance, name='mark_attendance_date'),

    # Add other views related to interests, attendance percentage, teacher schedules here too if you want
    path('interests/', views.view_interests, name='view_interests'),
    path('interests/edit/', views.edit_interests, name='edit_interests'),
    path('attendance/', views.attendance_percentage, name='attendance_percentage'),

    path('teacher/class_schedules/', views.teacher_class_schedules, name='teacher_class_schedules'),
    path('teacher/mark_attendance/<int:classschedule_id>/', views.mark_attendance, name='mark_attendance'),
    path('test/', views.test_view, name='test'),
    path('class/<int:classschedule_id>/qr_code/', generate_qr_code, name='qr_code_view'),
    path('scan_validate/', validate_qr_scan, name='validate_qr_scan'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard')
]
