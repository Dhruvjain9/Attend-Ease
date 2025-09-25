from django.urls import path
from . import views  

app_name = 'attendance'

urlpatterns = [
    # Student views
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('interests/', views.view_interests, name='view_interests'),
    path('interests/edit/', views.edit_interests, name='edit_interests'),
    path('attendance/', views.attendance_percentage, name='attendance_percentage'),

    # Teacher views
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/class_schedules/', views.teacher_class_schedules, name='teacher_class_schedules'),
    path('teacher/mark_attendance/<int:classschedule_id>/', views.mark_attendance, name='teacher_mark_attendance'),
    path('teacher/class/<int:schedule_id>/students/', views.class_students, name='class_students'),

    # Shared / attendance related
    path('classschedule/<int:classschedule_id>/attendance/', views.mark_attendance, name='student_mark_attendance'),
    path('classschedule/<int:classschedule_id>/attendance/<str:attendance_date>/', views.mark_attendance, name='mark_attendance_date'),
    
    # QR Code system
    path('class/<int:classschedule_id>/qr_code/', views.generate_qr_code, name='qr_code_view'),
    path('scan_validate/', views.validate_qr_scan, name='validate_qr_scan'),

    # Test
    path('test/', views.test_view, name='test'),
]
