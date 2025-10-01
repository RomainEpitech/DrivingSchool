from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from accounts.models import User, Student, Instructor
from scheduling.models import Appointment
from courses.models import Purchase
from accounts.forms import InstructorForm, StudentForm

def home(request):
    if request.user.is_authenticated:
        user = request.user
        today = timezone.now().date()
        
        # Récupérer le prochain rendez-vous
        if user.user_type == 'student':
            next_appointment = Appointment.objects.filter(
                student=user.student_profile,
                date__gte=today
            ).order_by('date', 'start_time').first()
            
            # Calcul de la progression (exemple simple)
            total_lessons = Appointment.objects.filter(student=user.student_profile).count()
            
            context = {
                'next_appointment': next_appointment,
                'total_lessons': total_lessons,
                'progress': min(total_lessons * 5, 100)  # 5% par leçon, max 100%
            }
            
        elif user.user_type == 'instructor':
            next_appointment = Appointment.objects.filter(
                instructor=user.instructor_profile,
                date__gte=today
            ).order_by('date', 'start_time').first()
            
            # Nombre d'élèves actifs
            active_students = Student.objects.filter(
                appointments__instructor=user.instructor_profile,
                appointments__date__gte=today
            ).distinct().count()
            
            context = {
                'next_appointment': next_appointment,
                'active_students': active_students,
                'total_teaching_hours': Appointment.objects.filter(instructor=user.instructor_profile).count() * 2  # Hypothèse: 2h par cours
            }
            
        else:  # secretary or admin
            next_appointment = Appointment.objects.filter(date__gte=today).order_by('date', 'start_time').first()
            active_users = User.objects.filter(is_active=True).count()
            
            context = {
                'next_appointment': next_appointment,
                'active_users': active_users
            }
        
        # Mock data for recent activities
        recent_activities = [
            {
                'icon': 'calendar-check',
                'title': 'Rendez-vous terminé',
                'description': 'Leçon de conduite sur autoroute',
                'date': timezone.now() - timezone.timedelta(days=1)
            },
            {
                'icon': 'shopping-cart',
                'title': 'Achat de forfait',
                'description': 'Forfait de 10 heures',
                'date': timezone.now() - timezone.timedelta(days=3)
            },
            {
                'icon': 'calendar-plus',
                'title': 'Nouveau rendez-vous',
                'description': 'Leçon de conduite en ville',
                'date': timezone.now() - timezone.timedelta(days=5)
            }
        ]
        
        context['recent_activities'] = recent_activities
        context['notifications_count'] = 2  # Mock notification count
        
        return render(request, 'accounts/home.html', context)
    else:
        return render(request, 'accounts/home.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Connexion réussie !')
            return redirect('home')
        else:
            messages.error(request, 'Identifiants invalides. Veuillez réessayer.')
    return render(request, 'accounts/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Vous avez été déconnecté.')
    return redirect('login')

@login_required
def profile_view(request):
    user = request.user
    context = {'user': user}
    
    if user.user_type == 'student':
        context['student'] = user.student_profile
    elif user.user_type == 'instructor':
        context['instructor'] = user.instructor_profile
        
    return render(request, 'accounts/profile.html', context)

@login_required
def student_list(request):
    # Vérifier les autorisations
    if request.user.user_type not in ['admin', 'secretary', 'instructor']:
        messages.error(request, "Vous n'avez pas l'autorisation de voir cette page.")
        return redirect('profile')
    
    # Filtrer les étudiants pour les instructeurs
    if request.user.user_type == 'instructor':
        # Montrer seulement les étudiants qui ont eu des rendez-vous avec cet instructeur
        instructor = request.user.instructor_profile
        student_ids = Appointment.objects.filter(instructor=instructor).values_list('student_id', flat=True).distinct()
        students = Student.objects.filter(id__in=student_ids)
    else:
        students = Student.objects.all()
    
    return render(request, 'accounts/student_list.html', {'students': students})

@login_required
def student_detail(request, pk):
    # Vérifier les autorisations
    if request.user.user_type not in ['admin', 'secretary', 'instructor']:
        messages.error(request, "Vous n'avez pas l'autorisation de voir cette page.")
        return redirect('profile')
    
    student = get_object_or_404(Student, pk=pk)
    
    # Si l'utilisateur est un instructeur, vérifier qu'il a bien ce student
    if request.user.user_type == 'instructor':
        instructor = request.user.instructor_profile
        if not Appointment.objects.filter(instructor=instructor, student=student).exists():
            messages.error(request, "Cet élève n'est pas sous votre responsabilité.")
            return redirect('student_list')
    
    # Récupérer les rendez-vous à venir
    today = timezone.now().date()
    upcoming_appointments = Appointment.objects.filter(
        student=student,
        date__gte=today
    ).order_by('date', 'start_time')
    
    # Récupérer l'historique des achats
    purchases = Purchase.objects.filter(student=student).order_by('-purchase_date')
    
    return render(request, 'accounts/student_detail.html', {
        'student': student,
        'upcoming_appointments': upcoming_appointments,
        'purchases': purchases
    })

@login_required
def instructor_list(request):
    # Vérifier les autorisations
    if request.user.user_type not in ['admin', 'secretary']:
        messages.error(request, "Vous n'avez pas l'autorisation de voir cette page.")
        return redirect('profile')
    
    instructors = Instructor.objects.all()
    return render(request, 'accounts/instructor_list.html', {'instructors': instructors})

@login_required
def instructor_detail(request, pk):
    # Vérifier les autorisations
    if request.user.user_type not in ['admin', 'secretary']:
        messages.error(request, "Vous n'avez pas l'autorisation de voir cette page.")
        return redirect('profile')
    
    instructor = get_object_or_404(Instructor, pk=pk)
    
    # Récupérer les élèves de cet instructeur
    student_ids = Appointment.objects.filter(instructor=instructor).values_list('student_id', flat=True).distinct()
    students = Student.objects.filter(id__in=student_ids)
    
    # Ajouter la date du dernier rendez-vous pour chaque étudiant
    for student in students:
        last_appointment = Appointment.objects.filter(
            instructor=instructor,
            student=student,
            date__lt=timezone.now().date()
        ).order_by('-date').first()
        
        student.last_appointment = last_appointment
    
    # Récupérer les rendez-vous à venir
    today = timezone.now().date()
    upcoming_appointments = Appointment.objects.filter(
        instructor=instructor,
        date__gte=today
    ).order_by('date', 'start_time')
    
    return render(request, 'accounts/instructor_detail.html', {
        'instructor': instructor,
        'students': students,
        'upcoming_appointments': upcoming_appointments
    })

@login_required
def instructor_create(request):
    # Vérifier les autorisations
    if request.user.user_type not in ['admin', 'secretary']:
        messages.error(request, "Vous n'avez pas l'autorisation d'effectuer cette action.")
        return redirect('instructor_list')
    
    if request.method == 'POST':
        form = InstructorForm(request.POST)
        if form.is_valid():
            instructor = form.save()
            messages.success(request, f"L'instructeur {instructor.user.get_full_name()} a été créé avec succès.")
            return redirect('instructor_detail', pk=instructor.pk)
    else:
        form = InstructorForm()
    
    return render(request, 'accounts/instructor_form.html', {
        'form': form,
        'is_new': True
    })

@login_required
def instructor_edit(request, pk):
    # Vérifier les autorisations
    if request.user.user_type not in ['admin', 'secretary']:
        messages.error(request, "Vous n'avez pas l'autorisation d'effectuer cette action.")
        return redirect('instructor_list')
    
    instructor = get_object_or_404(Instructor, pk=pk)
    
    if request.method == 'POST':
        form = InstructorForm(request.POST, instance=instructor)
        if form.is_valid():
            instructor = form.save()
            messages.success(request, f"L'instructeur {instructor.user.get_full_name()} a été mis à jour avec succès.")
            return redirect('instructor_detail', pk=instructor.pk)
    else:
        form = InstructorForm(instance=instructor)
    
    return render(request, 'accounts/instructor_form.html', {
        'form': form,
        'instructor': instructor,
        'is_new': False
    })

@login_required
def instructor_archive(request, pk):
    # Vérifier les autorisations
    if request.user.user_type not in ['admin', 'secretary']:
        messages.error(request, "Vous n'avez pas l'autorisation d'effectuer cette action.")
        return redirect('instructor_list')
    
    instructor = get_object_or_404(Instructor, pk=pk)
    
    if request.method == 'POST':
        # Archiver l'instructeur (désactiver l'utilisateur)
        user = instructor.user
        user.is_active = False
        user.save()
        messages.success(request, f"L'instructeur {user.get_full_name()} a été archivé avec succès.")
        return redirect('instructor_list')
    
    return render(request, 'accounts/instructor_confirm_archive.html', {
        'instructor': instructor
    })

@login_required
def student_create(request):
    # Vérifier les autorisations
    if request.user.user_type not in ['admin', 'secretary']:
        messages.error(request, "Vous n'avez pas l'autorisation d'effectuer cette action.")
        return redirect('student_list')
    
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            messages.success(request, f"L'élève {student.user.get_full_name()} a été créé avec succès.")
            return redirect('student_detail', pk=student.pk)
    else:
        form = StudentForm()
    
    return render(request, 'accounts/student_form.html', {
        'form': form,
        'is_new': True
    })

@login_required
def student_edit(request, pk):
    # Vérifier les autorisations
    if request.user.user_type not in ['admin', 'secretary']:
        messages.error(request, "Vous n'avez pas l'autorisation d'effectuer cette action.")
        return redirect('student_list')
    
    student = get_object_or_404(Student, pk=pk)
    
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            student = form.save()
            messages.success(request, f"L'élève {student.user.get_full_name()} a été mis à jour avec succès.")
            return redirect('student_detail', pk=student.pk)
    else:
        form = StudentForm(instance=student)
    
    return render(request, 'accounts/student_form.html', {
        'form': form,
        'student': student,
        'is_new': False
    })

@login_required
def student_archive(request, pk):
    # Vérifier les autorisations
    if request.user.user_type not in ['admin', 'secretary']:
        messages.error(request, "Vous n'avez pas l'autorisation d'effectuer cette action.")
        return redirect('student_list')
    
    student = get_object_or_404(Student, pk=pk)
    
    if request.method == 'POST':
        # Archiver l'élève (désactiver l'utilisateur)
        user = student.user
        user.is_active = False
        user.save()
        messages.success(request, f"L'élève {user.get_full_name()} a été archivé avec succès.")
        return redirect('student_list')
    
    return render(request, 'accounts/student_confirm_archive.html', {
        'student': student
    })