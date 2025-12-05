import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'advising_system.settings')
django.setup()

from django.contrib.auth.models import User
from advising_app.models import Student, Enrollment, Course

print("--- Users ---")
for user in User.objects.all():
    print(f"User: {user.username}, Is Staff: {user.is_staff}")
    if hasattr(user, 'student'):
        print(f"  Student ID: {user.student.student_id}")
        enrollments = Enrollment.objects.filter(student=user.student)
        print(f"  Enrollments ({enrollments.count()}):")
        for e in enrollments:
            print(f"    - {e.course.code} (ID: {e.course.id}) - {e.course.title}")
    print("-" * 20)

print("\n--- Courses with '103' in code ---")
courses = Course.objects.filter(code__icontains='103')
for c in courses:
    print(f"ID: {c.id}, Code: {c.code}, Title: {c.title}")
