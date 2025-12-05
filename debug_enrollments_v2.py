import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'advising_system.settings')
django.setup()

from django.contrib.auth.models import User
from advising_app.models import Student, Enrollment, Course

print("--- Debug Enrollments ---")
students = Student.objects.all()
for student in students:
    print(f"Student: {student.user.username} ({student.student_id})")
    enrollments = Enrollment.objects.filter(student=student)
    if enrollments.exists():
        for e in enrollments:
            print(f"  - Enrolled in: {e.course.code} (Sec: {e.course.section}) ID: {e.course.id}")
    else:
        print("  - No enrollments")

print("\n--- Courses with '103' ---")
courses = Course.objects.filter(code__icontains='103')
for c in courses:
    print(f"Code: {c.code}, Section: {c.section}, ID: {c.id}")
