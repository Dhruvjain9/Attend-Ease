#attendance - views.py

import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import modelformset_factory
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden
from .models import Attendance, ClassSchedule, Student
from .forms import AttendanceForm, StudentInterestsForm
import qrcode
from io import BytesIO
from django.http import HttpResponse
from django.utils import timezone
from .models import QRCodeSession, ClassSchedule
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Teacher, ClassSchedule
from django import messages

def teacher_required(user):
    return user.is_authenticated and hasattr(user, 'teacher')

@login_required
def interests(request):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return render(request, 'attendance/no_student_profile.html')

    if request.method == 'POST':
        form = StudentInterestsForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Your interests were updated successfully!")
            return redirect('attendance:interests')
    else:
        form = StudentInterestsForm(instance=student)

    return render(request, 'attendance/interests.html', {
        'student': student,
        'form': form,
    })

@login_required
def attendance_percentage(request):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return render(request, 'attendance/no_student_profile.html')

    total_classes = Attendance.objects.filter(student=student).count()
    present_classes = Attendance.objects.filter(student=student, status='Present').count()

    percentage = (present_classes / total_classes) * 100 if total_classes > 0 else 0

    return render(request, 'attendance/attendance_percentage.html', {
        'percentage': round(percentage, 2),
        'present_classes': present_classes,
        'total_classes': total_classes,
    })

@login_required
@user_passes_test(teacher_required)
def mark_attendance(request, classschedule_id):
    classschedule = get_object_or_404(ClassSchedule, id=classschedule_id)
    attendance_date = datetime.date.today()

    students = classschedule.students.all()
    AttendanceFormSet = modelformset_factory(Attendance, form=AttendanceForm, extra=0)

    for student in students:
        Attendance.objects.get_or_create(
            student=student,
            subject=classschedule.subject,
            date=attendance_date,
            defaults={'status': 'Absent', 'marked_by': request.user.teacher}
        )

    attendance_qs = Attendance.objects.filter(
        subject=classschedule.subject,
        date=attendance_date,
        student__in=students
    )

    if request.method == 'POST':
        formset = AttendanceFormSet(request.POST, queryset=attendance_qs)
        if formset.is_valid():
            formset.save()
            return redirect('teacher_class_schedules')
    else:
        formset = AttendanceFormSet(queryset=attendance_qs)

    return render(request, 'attendance/mark_attendance.html', {
        'formset': formset,
        'classschedule': classschedule,
        'attendance_date': attendance_date,
    })

@login_required
@user_passes_test(teacher_required)
def teacher_class_schedules(request):
    teacher = request.user.teacher
    schedules = teacher.class_schedules.all()
    return render(request, 'attendance/teacher_class_schedules.html', {'schedules': schedules})


@login_required
def student_dashboard(request):
    user = request.user
    try:
        student = user.student
    except Student.DoesNotExist:
        return render(request, 'attendance/no_student_profile.html')

    # Attendance summary
    total = Attendance.objects.filter(student=student).count()
    present = Attendance.objects.filter(student=student, status='Present').count()
    attendance_percentage = (present / total) * 100 if total > 0 else 0

    # Interests
    interests = student.interests

    # Class schedules - assuming student has a many-to-many relation with ClassSchedule
    class_schedules = ClassSchedule.objects.filter(students=student)

    context = {
        "student": student,
        "attendance_percentage": round(attendance_percentage, 2),
        "attendance_present": present,
        "attendance_total": total,
        "interests": interests,
        "class_schedules": class_schedules,
    }

    return render(request, 'attendance/student_dashboard.html', context)


def test_view(request):
    return render(request, "attendance/test.html")

def generate_qr_code(request, classschedule_id):
    try:
        # Get the class schedule object or return 404
        class_schedule = ClassSchedule.objects.get(id=classschedule_id)
    except ClassSchedule.DoesNotExist:
        return HttpResponse("Class schedule not found", status=404)

    # Get current aware datetime with timezone
    now = timezone.now()
    today = now.date()

    # Combine date with start and end time as naive datetime
    start_datetime_naive = datetime.datetime.combine(today, class_schedule.start_time)
    end_datetime_naive = datetime.datetime.combine(today, class_schedule.end_time)

    # Convert naive datetimes to aware datetimes using current timezone
    start_datetime = timezone.make_aware(start_datetime_naive, timezone.get_current_timezone())
    end_datetime = timezone.make_aware(end_datetime_naive, timezone.get_current_timezone())

    # Check if current time is within class schedule window
    if not (start_datetime <= now <= end_datetime):
        return HttpResponse("QR code not active now", status=403)

    # Check if an active QRCodeSession exists in the last 20 seconds
    twenty_seconds_ago = now - timezone.timedelta(seconds=20)
    qr_session = QRCodeSession.objects.filter(
        class_schedule=class_schedule,
        created_at__gte=twenty_seconds_ago
    ).first()

    # Create new QRCodeSession if none exists, provide start_time to avoid integrity error
    if not qr_session:
        qr_session = QRCodeSession.objects.create(
            class_schedule=class_schedule,
            start_time=timezone.now()
        )

    # Prepare QR code data with session ID
    data = f"qr_session_id:{qr_session.id}"

    # Generate and save QR code image to buffer
    qr_img = qrcode.make(data)
    buffer = BytesIO()
    qr_img.save(buffer)
    buffer.seek(0)

    # Return QR code image with MIME type image/png
    return HttpResponse(buffer, content_type="image/png")

@csrf_exempt
def validate_qr_scan(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)

    try:
        data = json.loads(request.body)
        qr_session_id = data.get("qr_session_id")
        student_id = data.get("student_id")
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({"error": "Invalid JSON data"}, status=400)

    if not qr_session_id or not student_id:
        return JsonResponse({"error": "Missing qr_session_id or student_id"}, status=400)

    try:
        qr_session = QRCodeSession.objects.get(id=qr_session_id)
    except QRCodeSession.DoesNotExist:
        return JsonResponse({"error": "Invalid or expired QR code"}, status=400)

    if (timezone.now() - qr_session.created_at).total_seconds() > 20:
        return JsonResponse({"error": "Expired QR code session"}, status=400)

    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return JsonResponse({"error": "Invalid student ID"}, status=400)

    class_schedule = qr_session.class_schedule
    if not class_schedule.students.filter(id=student.id).exists():
        return JsonResponse({"error": "Student not enrolled in this class"}, status=403)

    today = timezone.localdate()
    teacher = class_schedule.teacher  # Get teacher from class schedule

    attendance_record, created = Attendance.objects.get_or_create(
        student=student,
        subject=class_schedule.subject,
        date=today,
        defaults={"status": "Present", "marked_by": teacher}
    )

    if not created:
        return JsonResponse({"message": "Attendance already marked"}, status=200)

    return JsonResponse({"message": "Attendance marked successfully"}, status=200)

def teacher_dashboard(request):
    # Get logged-in teacher's user
    teacher = Teacher.objects.get(user=request.user)
    # Get their class schedules
    class_schedules = ClassSchedule.objects.filter(teacher=teacher)
    context = {
        'class_schedules': class_schedules
    }
    return render(request, 'attendance/teacher_dashboard.html', context)

def class_students(request, schedule_id):
    class_schedule = get_object_or_404(ClassSchedule, id=schedule_id)
    students = class_schedule.students.all()
    context = {
        'class_schedule': class_schedule,
        'students': students
    }
    return render(request, 'attendance/class_students.html', context)

