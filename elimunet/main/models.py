from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    USER_TYPES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=7, choices=USER_TYPES)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    def __str__(self):
        return self.user.username

class Classroom(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=10, unique=True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='classrooms')
    members = models.ManyToManyField(User, related_name='joined_classrooms')

    def __str__(self):
        return self.name

class Assignment(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    file = models.FileField(upload_to='assignments/', null=True, blank=True)
    due_date = models.DateTimeField()

    def __str__(self):
        return self.title

class Quiz(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    question = models.TextField()
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    option4 = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=255)

    def __str__(self):
        return self.title

class Announcement(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Material(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='materials/')
    description = models.TextField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='submissions/', null=True, blank=True)
    date_submitted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.assignment.title} - {self.student.username}'

class Grade(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    grade = models.IntegerField()

    def __str__(self):
        return f'{self.submission.assignment.title} - {self.submission.student.username} - {self.grade}'

class ClassComment(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.classroom.name}'

class PrivateMessage(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender.username} to {self.receiver.username}'
