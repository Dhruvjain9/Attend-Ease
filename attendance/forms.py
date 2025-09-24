from django import forms
from .models import Attendance, Student, ClassSchedule

class StudentInterestsForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['interests']
        widgets = {
            'interests': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }

class AttendanceForm(forms.ModelForm):
    status = forms.ChoiceField(
        choices=Attendance._meta.get_field('status').choices,
        widget=forms.RadioSelect
    )

    class Meta:
        model = Attendance
        fields = ['student', 'status']