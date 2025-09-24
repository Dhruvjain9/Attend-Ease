from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Student, Attendance, Teacher, Subject, ClassSchedule

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee_id', 'department']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['user', 'roll_number']

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'teacher']

@admin.register(ClassSchedule)
class ClassScheduleAdmin(admin.ModelAdmin):
    list_display = ['subject', 'day_of_week', 'start_time', 'end_time', 'room_number']

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'date', 'status', 'marked_by']
    list_filter = ['date', 'status', 'subject']
