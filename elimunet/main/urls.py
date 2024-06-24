from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('teacher_dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('create_classroom/', views.create_classroom, name='create_classroom'),
    path('join_classroom/', views.join_classroom, name='join_classroom'),
    path('classroom/<int:classroom_id>/create_assignment/', views.create_assignment, name='create_assignment'),
    path('classroom/<int:classroom_id>/create_quiz/', views.create_quiz, name='create_quiz'),
    path('classroom/<int:classroom_id>/create_announcement/', views.create_announcement, name='create_announcement'),
    path('classroom/<int:classroom_id>/upload_material/', views.upload_material, name='upload_material'),
    path('teacher_view_classroom/<int:classroom_id>/', views.teacher_view_classroom, name='teacher_view_classroom'),
    path('classroom/<int:classroom_id>/', views.view_classroom, name='view_classroom'),
    path('assignment/<int:assignment_id>/', views.view_assignment, name='view_assignment'),
    path('quiz/<int:quiz_id>/', views.view_quiz, name='view_quiz'),
    path('announcement/<int:announcement_id>/', views.view_announcement, name='view_announcement'),
    path('assignment/<int:assignment_id>/submit/', views.submit_assignment, name='submit_assignment'),
    path('quiz/<int:quiz_id>/submit/', views.submit_quiz, name='submit_quiz'),
    path('submission/<int:submission_id>/grade/', views.grade_submission, name='grade_submission'),
    path('classroom/<int:classroom_id>/post_comment/', views.post_comment, name='post_comment'),
    path('send_private_message/', views.send_private_message, name='send_private_message'),
    path('private_messages/', views.view_private_messages, name='view_private_messages'),
    path('announcements/', views.announcements, name='announcements'),
    path('edit_classroom/<int:classroom_id>/', views.edit_classroom, name='edit_classroom'),
    path('delete_classroom/<int:classroom_id>/', views.delete_classroom, name='delete_classroom'),
    path('classroom/<int:classroom_id>/delete_assignment/<int:assignment_id>/', views.delete_assignment, name='delete_assignment'),
    path('classroom/<int:classroom_id>/edit_assignment/<int:assignment_id>/', views.edit_assignment, name='edit_assignment'),
    path('generate_pdf_report/', views.generate_pdf_report, name='generate_pdf_report'),
    path('assignment/<int:assignment_id>/submissions/', views.view_assignment_submissions, name='view_assignment_submissions'),
    path('submission/<int:submission_id>/grade/', views.grade_submission, name='grade_submission'),
    path('grade_submission/<int:submission_id>/', views.grade_submission, name='grade_submission'),


]
