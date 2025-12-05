from django.db import models
from django.contrib.auth.models import User

class Faculty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    faculty_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.faculty_id} - {self.user.get_full_name()}"

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    current_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    cgpa = models.FloatField(default=0.0)
    advisor = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True, related_name='advisees')

    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name()}"

class Course(models.Model):
    DAYS_CHOICES = [
        ('Mon', 'Monday'),
        ('Tue', 'Tuesday'),
        ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'),
        ('Fri', 'Friday'),
        ('Sat', 'Saturday'),
        ('Sun', 'Sunday'),
    ]
    code = models.CharField(max_length=20)
    title = models.CharField(max_length=200)
    credit = models.FloatField()
    department = models.CharField(max_length=100)
    section = models.CharField(max_length=10, default='1')
    room = models.CharField(max_length=20, null=True, blank=True)
    capacity = models.IntegerField(default=40)
    assigned_faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True)
    day = models.CharField(max_length=3, choices=DAYS_CHOICES, default='Mon')
    start_time = models.TimeField(default='09:00')
    end_time = models.TimeField(default='10:30')

    class Meta:
        unique_together = ('code', 'section')

    def __str__(self):
        return f"{self.code} - {self.title} (Sec: {self.section}, {self.day} {self.start_time}-{self.end_time})"

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.student_id} enrolled in {self.course.code}"

class AdvisingRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request by {self.student.student_id} - {self.status}"

class PreferredCourse(models.Model):
    request = models.ForeignKey(AdvisingRequest, on_delete=models.CASCADE, related_name='preferred_courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    priority = models.IntegerField(help_text="1 is highest priority")

    class Meta:
        ordering = ['priority']

    def __str__(self):
        return f"{self.course.code} (Priority: {self.priority})"
