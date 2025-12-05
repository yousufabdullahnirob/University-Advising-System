from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('student/login/', views.student_login_view, name='student_login'),
    path('student/register/', views.student_register, name='student_register'),
    path('admin/login/', views.admin_login_view, name='admin_login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Faculty URLs
    path('faculty/login/', views.faculty_login_view, name='faculty_login'),
    path('faculty/register/', views.faculty_register, name='faculty_register'),
    path('faculty/dashboard/', views.faculty_dashboard, name='faculty_dashboard'),
    path('faculty/student/<str:student_id>/', views.advisee_detail, name='advisee_detail'),
    path('faculty/student/<str:student_id>/add-drop/', views.advisor_add_drop_course, name='advisor_add_drop_course'),
    path('faculty/course/<int:course_id>/update-capacity/', views.update_course_capacity, name='update_course_capacity'),
    
    # Student URLs
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/advising/', views.advising_view, name='advising_view'),
    path('student/courses/', views.course_list, name='course_list'),
    path('student/request/', views.submit_advising_request, name='submit_advising_request'),
    
    # Admin URLs
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/courses/', views.manage_courses, name='manage_courses'),
    path('admin/courses/delete/<int:course_id>/', views.delete_course, name='delete_course'),
    path('admin/requests/', views.manage_requests, name='manage_requests'),
    path('admin/requests/approve/<int:request_id>/', views.approve_request, name='approve_request'),
    path('admin/requests/reject/<int:request_id>/', views.reject_request, name='reject_request'),
    path('admin/assign-advisor/', views.admin_assign_advisor, name='admin_assign_advisor'),
]
