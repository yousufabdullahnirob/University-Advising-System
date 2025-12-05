from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Course, AdvisingRequest, PreferredCourse, Student, Enrollment, Faculty
from .forms import StudentRegistrationForm, FacultyRegistrationForm
from django.db.models import Q, Count, IntegerField
from django.db.models.functions import Cast

# --- Authentication ---

def landing_page(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        else:
            return redirect('student_dashboard')
    return render(request, 'advising_app/landing.html')

def student_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.is_staff:
                login(request, user)
                return redirect('student_dashboard')
            else:
                messages.error(request, "This login is for Students only.")
        else:
            # Form errors are handled by the template
            pass
    else:
        form = AuthenticationForm()
    return render(request, 'advising_app/student_login.html', {'form': form})

def admin_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_staff:
                login(request, user)
                return redirect('admin_dashboard')
            else:
                messages.error(request, "This login is for Admins only.")
    else:
        form = AuthenticationForm()
    return render(request, 'advising_app/admin_login.html', {'form': form})

def faculty_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Check if user has a faculty profile
            if hasattr(user, 'faculty'):
                login(request, user)
                return redirect('faculty_dashboard')
            else:
                messages.error(request, "This login is for Faculty only.")
    else:
        form = AuthenticationForm()
    return render(request, 'advising_app/faculty_login.html', {'form': form})

def faculty_register(request):
    if request.method == 'POST':
        form = FacultyRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Faculty registration successful. Please login.")
            return redirect('faculty_login')
    else:
        form = FacultyRegistrationForm()
    return render(request, 'advising_app/faculty_register.html', {'form': form})

def student_register(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful. Please login.")
            return redirect('student_login')
    else:
        form = StudentRegistrationForm()
    return render(request, 'advising_app/student_register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('landing_page')

# --- Student Views ---

@login_required
def student_dashboard(request):
    """
    Displays the student's dashboard with enrolled courses and current balance.
    """
    if request.user.is_staff:
        return redirect('admin_dashboard')
    
    try:
        student = request.user.student
        enrollments = student.enrollments.all().select_related('course')
        # Calculate total credit and payable amount (6000 per credit)
        total_credit = sum(e.course.credit for e in enrollments)
        payable_amount = total_credit * 6000
        
        # Update student balance (simple logic for demo)
        student.current_balance = payable_amount
        student.save()
        
    except Student.DoesNotExist:
        student = None
        enrollments = []
        payable_amount = 0
        
    return render(request, 'advising_app/student/dashboard.html', {
        'student': student,
        'enrollments': enrollments,
        'payable_amount': payable_amount
    })

@login_required
def advising_view(request):
    """
    Handles the student advising process, including course selection,
    conflict detection (time, credit limit), and enrollment.
    """
    try:
        student = request.user.student
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('student_dashboard')

    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        action = request.POST.get('action')
        course = get_object_or_404(Course, id=course_id)
        
        if action == 'drop':
            enrollment = Enrollment.objects.filter(student=student, course=course).first()
            if enrollment:
                enrollment.delete()
                messages.success(request, f"Successfully dropped {course.code}")
            else:
                messages.error(request, f"Not enrolled in {course.code}")
            return redirect('advising_view')

        # Default to 'add' logic
        # Check if already enrolled in this specific section
        if Enrollment.objects.filter(student=student, course=course).exists():
            messages.warning(request, f"Already enrolled in {course.code}")
            return redirect('advising_view')

        # Check if already enrolled in any section of this course code
        if Enrollment.objects.filter(student=student, course__code=course.code).exists():
            messages.error(request, f"You have already taken {course.code}. You cannot retake the same course.")
            return redirect('advising_view')

        # Check credit limit
        current_enrollments = Enrollment.objects.filter(student=student)
        current_credits = sum(e.course.credit for e in current_enrollments)
        if current_credits + course.credit > 15:
            messages.error(request, f"Cannot enroll. Total credits would exceed 15. Current: {current_credits}, Course: {course.credit}")
            return redirect('advising_view')
            
        # Check for time clash
        clashing_enrollment = Enrollment.objects.filter(
            student=student,
            course__day=course.day,
            course__start_time__lt=course.end_time,
            course__end_time__gt=course.start_time
        ).first()
        
        if clashing_enrollment:
            messages.error(request, f"Time clash with {clashing_enrollment.course.code} ({clashing_enrollment.course.day} {clashing_enrollment.course.start_time})")
            return redirect('advising_view')

        # Check capacity
        current_count = Enrollment.objects.filter(course=course).count()
        if current_count >= course.capacity:
            messages.error(request, f"Course {course.code} is full.")
            return redirect('advising_view')
            
        # Enroll
        Enrollment.objects.create(student=student, course=course)
        messages.success(request, f"Successfully enrolled in {course.code}")
        return redirect('advising_view')

    # Get all courses with enrollment count, ordered by code and section (numerically)
    all_courses = Course.objects.annotate(
        enrolled_count=Count('enrollment'),
        section_int=Cast('section', IntegerField())
    ).order_by('code', 'section_int')
    
    # Get enrolled course IDs and Codes
    enrolled_courses = Enrollment.objects.filter(student=student)
    enrolled_course_ids = enrolled_courses.values_list('course_id', flat=True)
    enrolled_course_codes = enrolled_courses.values_list('course__code', flat=True)
    
    # Prepare course list with status (Enrolled, Clash, Available)
    courses_with_status = []
    for course in all_courses:
        status = 'Available'
        if course.id in enrolled_course_ids:
            status = 'Enrolled'
        elif course.code in enrolled_course_codes:
            status = 'Taken'
        elif course.enrolled_count >= course.capacity:
            status = 'Full'
        else:
            # Check for clash
            is_clash = Enrollment.objects.filter(
                student=student,
                course__day=course.day,
                course__start_time__lt=course.end_time,
                course__end_time__gt=course.start_time
            ).exists()
            if is_clash:
                status = 'Clash'
        
        courses_with_status.append({
            'course': course,
            'status': status,
            'enrolled_count': course.enrolled_count
        })
        
    # Calculate totals for display
    total_credits = sum(e.course.credit for e in Enrollment.objects.filter(student=student))
    total_cost = total_credits * 6000

    return render(request, 'advising_app/student/advising.html', {
        'courses': courses_with_status,
        'total_credits': total_credits,
        'total_cost': total_cost
    })

@login_required
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'advising_app/student/course_list.html', {'courses': courses})

@login_required
def submit_advising_request(request):
    if request.method == 'POST':
        selected_course_ids = request.POST.getlist('courses')
        if not selected_course_ids:
            messages.error(request, "Please select at least one course.")
            return redirect('submit_advising_request')
        
        # Check credit limit
        selected_courses = Course.objects.filter(id__in=selected_course_ids)
        total_credits = sum(c.credit for c in selected_courses)
        if total_credits > 15:
             messages.error(request, f"Cannot submit request. Total credits exceed 15. Selected: {total_credits}")
             return redirect('submit_advising_request')
        
        try:
            student = request.user.student
        except Student.DoesNotExist:
             messages.error(request, "Student profile not found.")
             return redirect('student_dashboard')

        # Check if pending request exists
        if AdvisingRequest.objects.filter(student=student, status='Pending').exists():
            messages.warning(request, "You already have a pending request.")
            return redirect('student_dashboard')

        advising_request = AdvisingRequest.objects.create(student=student)
        
        for priority, course_id in enumerate(selected_course_ids, start=1):
            course = get_object_or_404(Course, id=course_id)
            PreferredCourse.objects.create(request=advising_request, course=course, priority=priority)
            
        messages.success(request, "Advising request submitted successfully!")
        return redirect('student_dashboard')
    
    courses = Course.objects.all()
    return render(request, 'advising_app/student/request_form.html', {'courses': courses})

# --- Faculty Views ---

@login_required
def faculty_dashboard(request):
    try:
        faculty = request.user.faculty
        assigned_courses = Course.objects.filter(assigned_faculty=faculty).order_by('code', 'section')
        advisees = Student.objects.filter(advisor=faculty)
        
        # Search functionality
        query = request.GET.get('q')
        if query:
            advisees = advisees.filter(student_id__icontains=query)
            
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect('landing_page')
        
    return render(request, 'advising_app/faculty/dashboard.html', {
        'faculty': faculty,
        'courses': assigned_courses,
        'advisees': advisees
    })

@login_required
def advisee_detail(request, student_id):
    try:
        faculty = request.user.faculty
        student = get_object_or_404(Student, student_id=student_id)
        
        # Check if this student is an advisee of the logged-in faculty
        if student.advisor != faculty:
            messages.error(request, "You are not the advisor for this student.")
            return redirect('faculty_dashboard')
            
        # Enforce Department Check
        if student.department != faculty.department:
             messages.error(request, "You can only advise students from your own department.")
             return redirect('faculty_dashboard')

        enrollments = Enrollment.objects.filter(student=student).select_related('course')
        total_credits = sum(e.course.credit for e in enrollments)
        
        # Get all courses for add/drop functionality (simplified for advisor)
        all_courses = Course.objects.all().order_by('code', 'section')
        
    except Faculty.DoesNotExist:
        return redirect('landing_page')
        
    return render(request, 'advising_app/faculty/advisee_detail.html', {
        'student': student,
        'enrollments': enrollments,
        'total_credits': total_credits,
        'all_courses': all_courses
    })

@login_required
def advisor_add_drop_course(request, student_id):
    if request.method == 'POST':
        try:
            faculty = request.user.faculty
            student = get_object_or_404(Student, student_id=student_id)
            
            if student.advisor != faculty:
                messages.error(request, "Unauthorized.")
                return redirect('faculty_dashboard')
                
            # Enforce Department Check
            if student.department != faculty.department:
                 messages.error(request, "You can only advise students from your own department.")
                 return redirect('faculty_dashboard')

            course_id = request.POST.get('course_id')
            action = request.POST.get('action')
            course = get_object_or_404(Course, id=course_id)
            
            if action == 'drop':
                Enrollment.objects.filter(student=student, course=course).delete()
                messages.success(request, f"Dropped {course.code} for {student.student_id}")
            elif action == 'add':
                # Basic checks for advisor override (skip capacity/clash for now or keep them? User said "dewaite parbe", implies power)
                # Let's keep basic checks but maybe allow override? For now, standard checks.
                
                # Check if already enrolled
                if Enrollment.objects.filter(student=student, course=course).exists():
                     messages.warning(request, "Already enrolled.")
                else:
                     Enrollment.objects.create(student=student, course=course)
                     messages.success(request, f"Added {course.code} for {student.student_id}")
                     
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            
    return redirect('advisee_detail', student_id=student_id)

@login_required
def update_course_capacity(request, course_id):
    if request.method == 'POST':
        try:
            faculty = request.user.faculty
            course = get_object_or_404(Course, id=course_id)
            
            if course.assigned_faculty != faculty:
                messages.error(request, "You can only update your own courses.")
                return redirect('faculty_dashboard')
                
            new_capacity = request.POST.get('capacity')
            if new_capacity:
                course.capacity = int(new_capacity)
                course.save()
                messages.success(request, f"Capacity for {course.code} updated to {new_capacity}")
                
        except Exception as e:
             messages.error(request, f"Error: {str(e)}")
             
    return redirect('faculty_dashboard')

# --- Admin Views ---

def is_admin(user):
    return user.is_staff

@user_passes_test(is_admin)
def admin_dashboard(request):
    total_courses = Course.objects.count()
    pending_requests = AdvisingRequest.objects.filter(status='Pending').count()
    return render(request, 'advising_app/admin/dashboard.html', {
        'total_courses': total_courses,
        'pending_requests': pending_requests
    })

@user_passes_test(is_admin)
def manage_courses(request):
    courses = Course.objects.all()
    if request.method == 'POST':
        # Simple add course logic for demo
        code = request.POST.get('code')
        title = request.POST.get('title')
        credit = request.POST.get('credit')
        department = request.POST.get('department')
        if code and title and credit:
            Course.objects.create(code=code, title=title, credit=credit, department=department)
            messages.success(request, "Course added.")
            return redirect('manage_courses')
            
    return render(request, 'advising_app/admin/manage_courses.html', {'courses': courses})

@user_passes_test(is_admin)
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    course.delete()
    messages.success(request, "Course deleted.")
    return redirect('manage_courses')

@user_passes_test(is_admin)
def manage_requests(request):
    requests = AdvisingRequest.objects.filter(status='Pending')
    return render(request, 'advising_app/admin/manage_requests.html', {'requests': requests})

@user_passes_test(is_admin)
def approve_request(request, request_id):
    advising_request = get_object_or_404(AdvisingRequest, id=request_id)
    advising_request.status = 'Approved'
    advising_request.save()
    messages.success(request, f"Request for {advising_request.student} approved.")
    return redirect('manage_requests')

@user_passes_test(is_admin)
def reject_request(request, request_id):
    advising_request = get_object_or_404(AdvisingRequest, id=request_id)
    advising_request.status = 'Rejected'
    advising_request.save()
    messages.success(request, f"Request for {advising_request.student} rejected.")
    return redirect('manage_requests')

@user_passes_test(is_admin)
def admin_assign_advisor(request):
    departments = Student.objects.values_list('department', flat=True).distinct()
    
    selected_dept = request.GET.get('department')
    students = []
    faculty_members = []
    
    if selected_dept:
        # Get students without advisors (or all? usually assign to those who need it)
        # Let's show all students in dept to allow re-assignment, but maybe highlight unassigned
        students = Student.objects.filter(department=selected_dept).order_by('student_id')
        
        # Get faculty in dept with their current advisee count
        faculty_members = Faculty.objects.filter(department=selected_dept).annotate(
            advisee_count=Count('advisees')
        )
        
    if request.method == 'POST':
        advisor_id = request.POST.get('advisor_id')
        student_ids = request.POST.getlist('student_ids')
        
        if advisor_id and student_ids:
            advisor = get_object_or_404(Faculty, id=advisor_id)
            
            # Check capacity (Limit 50)
            current_count = advisor.advisees.count()
            to_add_count = len(student_ids)
            
            if current_count + to_add_count > 50:
                messages.error(request, f"Cannot assign. Advisor limit (50) would be exceeded. Current: {current_count}, Adding: {to_add_count}")
            else:
                Student.objects.filter(id__in=student_ids).update(advisor=advisor)
                messages.success(request, f"Successfully assigned {to_add_count} students to {advisor.user.get_full_name()}")
                
        return redirect(f"{request.path}?department={selected_dept}")

    return render(request, 'advising_app/admin/assign_advisor.html', {
        'departments': departments,
        'selected_dept': selected_dept,
        'students': students,
        'faculty_members': faculty_members
    })
