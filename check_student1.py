import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'advising_system.settings')
django.setup()

from advising_app.models import Student, Enrollment

print("--- Student1 Enrollments ---")
try:
    student = Student.objects.get(user__username='student1')
    enrollments = Enrollment.objects.filter(student=student)
    if enrollments.exists():
        for e in enrollments:
            print(f"Enrolled: {e.course.code} (Sec: {e.course.section}) ID: {e.course.id}")
    else:
        print("No enrollments found for student1.")
except Student.DoesNotExist:
    print("student1 profile not found.")
