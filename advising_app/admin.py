from django.contrib import admin
from .models import Student, Faculty, Course, AdvisingRequest, PreferredCourse, Enrollment

admin.site.register(Student)
admin.site.register(Faculty)
admin.site.register(Course)
admin.site.register(AdvisingRequest)
admin.site.register(PreferredCourse)
admin.site.register(Enrollment)
