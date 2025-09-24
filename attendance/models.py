from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    roll_number = models.CharField(max_length=20, unique=True)
    interests = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class ClassSchedule(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='class_schedules')
    day_of_week = models.CharField(max_length=10, choices=[
        ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday')
    ])


    start_time = models.TimeField()
    end_time = models.TimeField()
    room_number = models.CharField(max_length=20)
    students = models.ManyToManyField(Student, blank=True)
    
    def __str__(self):
        return f"{self.subject.name} - {self.day_of_week} {self.start_time} - Room {self.room_number}"

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=10, choices=[('Present', 'Present'), ('Absent', 'Absent')])
    time_marked = models.DateTimeField(auto_now_add=True)
    marked_by = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.student.user.first_name} - {self.subject.name} - {self.date} - {self.status}"
    
    #class Meta:-
       #unique_together = ['student', 'subject', 'date']

class QRCodeSession(models.Model):
    class_schedule = models.ForeignKey('ClassSchedule', on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def is_active(self):
        # QR code valid for 20 seconds after created_at
        return (timezone.now() - self.created_at).total_seconds() <= 20
    def __str__(self):
        return f"QR Session for {self.class_schedule} at {self.created_at}"
