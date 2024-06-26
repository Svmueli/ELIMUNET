from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import (
    UserRegistrationForm, UserProfileForm, ClassroomCreationForm, JoinClassroomForm,
    AssignmentForm, QuizForm, AnnouncementForm, ClassCommentForm, PrivateMessageForm,
    MaterialForm, GradeForm, SubmissionForm
)
from .models import (
    Classroom, Assignment, Quiz, Announcement, Submission, Grade, ClassComment, PrivateMessage,
    Material, UserProfile, 
)
import random
import string
from django.http import FileResponse, HttpResponse
from reportlab.pdfgen import canvas
import io

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from django.http import FileResponse
import io

def home(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin:index')
        elif request.user.userprofile.user_type == 'teacher':
            return redirect('teacher_dashboard')
        else:
            return redirect('student_dashboard')
    form = AuthenticationForm()
    return render(request, 'main/home.html', {'form': form})

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            new_profile = profile_form.save(commit=False)
            new_profile.user = new_user
            new_profile.save()
            messages.success(request, 'Registration successful. Please log in.')
            return redirect('login')
    else:
        user_form = UserRegistrationForm()
        profile_form = UserProfileForm()
    return render(request, 'main/register.html', {'user_form': user_form, 'profile_form': profile_form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_staff:
                return redirect('admin:index')
            elif user.userprofile.user_type == 'teacher':
                return redirect('teacher_dashboard')
            else:
                return redirect('student_dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'main/login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    return redirect('home')

def generate_unique_code():
    length = 10
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        if not Classroom.objects.filter(code=code).exists():
            break
    return code

@login_required
def create_classroom(request):
    classroom_code = None
    if request.method == 'POST':
        form = ClassroomCreationForm(request.POST)
        if form.is_valid():
            classroom = form.save(commit=False)
            classroom.teacher = request.user
            classroom.code = generate_unique_code()
            classroom.save()
            classroom.members.add(request.user)
            classroom_code = classroom.code
    else:
        form = ClassroomCreationForm()
    return render(request, 'main/create_classroom.html', {'form': form, 'classroom_code': classroom_code})

@login_required
def edit_classroom(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)
    if request.method == 'POST':
        form = ClassroomCreationForm(request.POST, instance=classroom)
        if form.is_valid():
            form.save()
            messages.success(request, 'Classroom updated successfully.')
            return redirect('teacher_dashboard')
    else:
        form = ClassroomCreationForm(instance=classroom)
    return render(request, 'main/edit_classroom.html', {'form': form, 'classroom': classroom})

@login_required
def delete_classroom(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)
    if request.method == 'POST':
        classroom.delete()
        messages.success(request, 'Classroom deleted successfully.')
        return redirect('teacher_dashboard')
    return render(request, 'main/delete_classroom.html', {'classroom': classroom})

@login_required
def join_classroom(request):
    if request.method == 'POST':
        form = JoinClassroomForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                classroom = Classroom.objects.get(code=code)
                classroom.members.add(request.user)
                if request.user.is_staff:
                    return redirect('admin_dashboard')
                return redirect('student_dashboard')
            except Classroom.DoesNotExist:
                form.add_error('code', 'Invalid classroom code')
    else:
        form = JoinClassroomForm()
    return render(request, 'main/join_classroom.html', {'form': form})

@login_required
def teacher_dashboard(request):
    classrooms = Classroom.objects.filter(teacher=request.user)
    return render(request, 'main/teacher_dashboard.html', {
        'classrooms': classrooms,
        'userprofile': request.user.userprofile,
    })

@login_required
def student_dashboard(request):
    classrooms = Classroom.objects.filter(members=request.user)
    assignments = Assignment.objects.filter(classroom__in=classrooms)
    return render(request, 'main/student_dashboard.html', {
        'classrooms': classrooms,
        'assignments': assignments,
        'userprofile': request.user.userprofile,
    })

@login_required
def admin_dashboard(request):
    classrooms = Classroom.objects.all()
    return render(request, 'main/admin_dashboard.html', {
        'classrooms': classrooms,
        'userprofile': request.user.userprofile,
    })

@login_required
def create_assignment(request, classroom_id):
    classroom = Classroom.objects.get(id=classroom_id)
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.classroom = classroom
            assignment.save()
            return redirect('view_classroom', classroom_id=classroom.id)
    else:
        form = AssignmentForm()
    return render(request, 'main/create_assignment.html', {'form': form, 'classroom': classroom})

@login_required
def delete_assignment(request, classroom_id, assignment_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)
    assignment = get_object_or_404(Assignment, id=assignment_id, classroom=classroom)
    if request.method == 'POST':
        assignment.delete()
        return redirect('view_classroom', classroom_id=classroom.id)
    return render(request, 'main/delete_assignment.html', {'assignment': assignment, 'classroom': classroom})

@login_required
def edit_assignment(request, classroom_id, assignment_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)
    assignment = get_object_or_404(Assignment, id=assignment_id, classroom=classroom)
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES, instance=assignment)
        if form.is_valid():
            form.save()
            return redirect('view_classroom', classroom_id=classroom.id)
    else:
        form = AssignmentForm(instance=assignment)
    return render(request, 'main/edit_assignment.html', {'form': form, 'classroom': classroom, 'assignment': assignment})

@login_required
def create_quiz(request, classroom_id):
    classroom = Classroom.objects.get(id=classroom_id)
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.classroom = classroom
            quiz.save()
            if request.user.is_staff:
                return redirect('admin_dashboard')
            return redirect('teacher_dashboard')
    else:
        form = QuizForm()
    return render(request, 'main/create_quiz.html', {'form': form, 'classroom': classroom})

@login_required
def create_announcement(request, classroom_id):
    classroom = Classroom.objects.get(id=classroom_id)
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.classroom = classroom
            announcement.save()
            if request.user.is_staff:
                return redirect('admin_dashboard')
            return redirect('teacher_dashboard')
    else:
        form = AnnouncementForm()
    return render(request, 'main/create_announcement.html', {'form': form, 'classroom': classroom})

@login_required
def upload_material(request, classroom_id):
    classroom = Classroom.objects.get(id=classroom_id)
    if request.method == 'POST':
        form = MaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.classroom = classroom
            material.save()
            if request.user.is_staff:
                return redirect('admin_dashboard')
            return redirect('teacher_dashboard')
    else:
        form = MaterialForm()
    return render(request, 'main/upload_material.html', {'form': form, 'classroom': classroom})

@login_required
def view_classroom(request, classroom_id):
    classroom = Classroom.objects.get(id=classroom_id)
    assignments = Assignment.objects.filter(classroom=classroom)
    quizzes = Quiz.objects.filter(classroom=classroom)
    announcements = Announcement.objects.filter(classroom=classroom)
    materials = Material.objects.filter(classroom=classroom)
    return render(request, 'main/view_classroom.html', {
        'classroom': classroom,
        'assignments': assignments,
        'quizzes': quizzes,
        'announcements': announcements,
        'materials': materials,
    })

@login_required
def grade_submission(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    if request.method == 'POST':
        form = GradeForm(request.POST)
        if form.is_valid():
            grade = form.save(commit=False)
            grade.submission = submission
            grade.save()
            messages.success(request, 'Submission graded successfully.')
            return redirect('view_assignment_submissions', assignment_id=submission.assignment.id)
    else:
        form = GradeForm()
    return render(request, 'main/grade_submission.html', {'form': form, 'submission': submission})

@login_required
def view_assignment_submissions(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    submissions = Submission.objects.filter(assignment=assignment)

    if request.user != assignment.classroom.teacher:
        messages.error(request, 'You are not authorized to view this page.')
        return redirect('teacher_dashboard')

    return render(request, 'main/view_assignment_submissions.html', {
        'assignment': assignment,
        'submissions': submissions,
    })

@login_required
def view_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    submissions = Submission.objects.filter(assignment=assignment, student=request.user)
    return render(request, 'main/view_assignment.html', {
        'assignment': assignment,
        'submissions': submissions,
    })


@login_required
def view_quiz(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    return render(request, 'main/view_quiz.html', {'quiz': quiz})

@login_required
def view_announcement(request, announcement_id):
    announcement = Announcement.objects.get(id=announcement_id)
    return render(request, 'main/view_announcement.html', {'announcement': announcement})

@login_required
def submit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.student = request.user
            submission.save()
            messages.success(request, 'Assignment submitted successfully.')
            return redirect('view_assignments', assignment_id=assignment.id)
    else:
        form = SubmissionForm()
    return render(request, 'main/submit_assignment.html', {'form': form, 'assignment': assignment})

@login_required
def submit_quiz(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    if request.method == 'POST':
        selected_option = request.POST.get('answer')
        if selected_option == quiz.correct_option:
            result = "Correct"
        else:
            result = "Incorrect"
        return render(request, 'main/quiz_result.html', {'quiz': quiz, 'result': result})
    return redirect('view_quiz', quiz_id=quiz.id)


@login_required
def post_comment(request, classroom_id):
    classroom = Classroom.objects.get(id=classroom_id)
    if request.method == 'POST':
        form = ClassCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.classroom = classroom
            comment.user = request.user
            comment.save()
            return redirect('view_classroom', classroom_id=classroom.id)
    else:
        form = ClassCommentForm()
    return render(request, 'main/post_comment.html', {'form': form, 'classroom': classroom})

@login_required
def send_private_message(request):
    if request.method == 'POST':
        form = PrivateMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            return redirect('dashboard')
    else:
        form = PrivateMessageForm()
    return render(request, 'main/send_private_message.html', {'form': form})

@login_required
def announcements(request):
    announcements = Announcement.objects.filter(classroom__members=request.user)
    return render(request, 'main/view_announcements.html', {'announcements': announcements})

@login_required
def view_private_messages(request):
    received_messages = PrivateMessage.objects.filter(receiver=request.user)
    sent_messages = PrivateMessage.objects.filter(sender=request.user)
    return render(request, 'main/view_private_messages.html', {
        'received_messages': received_messages,
        'sent_messages': sent_messages
    })

@login_required
def teacher_view_classroom(request, classroom_id):
    classroom = Classroom.objects.get(id=classroom_id)
    return render(request, 'main/teacher_view_classroom.html', {'classroom': classroom})

@login_required
def generate_pdf_report(request):
    if not request.user.userprofile.user_type == 'teacher':
        messages.error(request, "You are not authorized to view this report.")
        return redirect('teacher_dashboard')

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Add title
    title = Paragraph("Teacher Report:Current Classes", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # Fetch teacher's classrooms and details
    classrooms = Classroom.objects.filter(teacher=request.user)
    for classroom in classrooms:
        classroom_title = Paragraph(f"Classroom: {classroom.name}", styles['Heading3'])
        elements.append(classroom_title)
        elements.append(Spacer(1, 12))

        # Assignments in the classroom
        assignments = Assignment.objects.filter(classroom=classroom)
        for assignment in assignments:
            assignment_title = Paragraph(f"Assignment: {assignment.title}", styles['Heading4'])
            elements.append(assignment_title)

            # Students and their grades
            submissions = Submission.objects.filter(assignment=assignment)
            data = [["Student", "Grade"]]
            for submission in submissions:
                grade = submission.grade.grade if hasattr(submission, 'grade') else 'Not graded'
                data.append([submission.student.username, grade])

            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))

            elements.append(table)
            elements.append(Spacer(1, 12))

        elements.append(Spacer(1, 24))

    doc.build(elements)
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='teacher_report.pdf')