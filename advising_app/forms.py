from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import Student, Faculty

class StudentRegistrationForm(UserCreationForm):
    department = forms.CharField(max_length=100, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            
            # Auto-generate Student ID
            import datetime
            current_year = datetime.date.today().year
            
            # Find the last student ID from the current year
            last_student = Student.objects.filter(student_id__startswith=str(current_year)).order_by('student_id').last()
            
            if last_student:
                # Extract the sequence number and increment
                last_id = last_student.student_id
                sequence = int(last_id[4:]) + 1
                new_student_id = f"{current_year}{sequence:04d}"
            else:
                # Start with 0001 for the current year
                new_student_id = f"{current_year}0001"

            Student.objects.create(
                user=user,
                student_id=new_student_id,
                department=self.cleaned_data['department']
            )
        return user

class FacultyRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    faculty_id = forms.CharField(max_length=20, label="Faculty ID (Q Code)")
    department = forms.CharField(max_length=100)
    designation = forms.CharField(max_length=100)

    class Meta:
        model = Faculty
        fields = ['faculty_id', 'department', 'designation']

    def clean_faculty_id(self):
        faculty_id = self.cleaned_data.get('faculty_id')
        if not faculty_id.startswith('Q1'):
            raise ValidationError("Faculty ID must start with 'Q1'")
        return faculty_id

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name']
        )
        faculty = super().save(commit=False)
        faculty.user = user
        if commit:
            faculty.save()
        return faculty
