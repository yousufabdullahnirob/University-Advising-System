import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'advising_system.settings')
django.setup()

from advising_app.models import Student, Enrollment

print("--- All Students Enrollments ---")
students = Student.objects.all()
for student in students:
    count = Enrollment.objects.filter(student=student).count()
    print(f"Student: {student.user.username} ({student.student_id}) - Enrollments: {count}")
    if count > 0:
        enrollments = Enrollment.objects.filter(student=student)
        codes = [e.course.code for e in enrollments]
        print(f"  Codes: {codes}")
