import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'advising_system.settings')
django.setup()

from advising_app.models import Student, Enrollment

try:
    student = Student.objects.get(user__username='@sadaf')
    enrollments = Enrollment.objects.filter(student=student, course__code='CSE103')
    for e in enrollments:
        print(f"You are enrolled in: {e.course.code} Section {e.course.section} (Day: {e.course.day}, Time: {e.course.start_time})")
except Student.DoesNotExist:
    print("User not found")
