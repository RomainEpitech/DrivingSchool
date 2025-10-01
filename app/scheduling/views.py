from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from scheduling.models import Appointment
from accounts.models import Student, Instructor
from django.http import HttpResponseForbidden

@login_required
def appointment_list(request):
    user = request.user
    today = timezone.now().date()
    
    if user.user_type == 'student':
        # Les étudiants ne voient que leurs rendez-vous
        appointments = Appointment.objects.filter(student=user.student_profile)
    elif user.user_type == 'instructor':
        # Les instructeurs ne voient que leurs rendez-vous
        appointments = Appointment.objects.filter(instructor=user.instructor_profile)
    elif user.user_type in ['secretary', 'admin']:
        # Les secrétaires et admins voient tous les rendez-vous
        appointments = Appointment.objects.all()
    else:
        messages.error(request, "Vous n'avez pas l'autorisation de voir cette page.")
        return redirect('profile')
    
    # Séparer les rendez-vous passés et futurs
    future_appointments = appointments.filter(date__gte=today).order_by('date', 'start_time')
    past_appointments = appointments.filter(date__lt=today).order_by('-date', 'start_time')
    
    return render(request, 'scheduling/appointment_list.html', {
        'future_appointments': future_appointments,
        'past_appointments': past_appointments
    })

@login_required
def appointment_detail(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    today_date = timezone.now().date()
    
    # Vérification des permissions
    user = request.user
    if user.user_type == 'student' and appointment.student.user != user:
        messages.error(request, "Vous n'avez pas l'autorisation de voir ce rendez-vous.")
        return redirect('appointment_list')
    elif user.user_type == 'instructor' and appointment.instructor.user != user:
        messages.error(request, "Vous n'avez pas l'autorisation de voir ce rendez-vous.")
        return redirect('appointment_list')
    
    return render(request, 'scheduling/appointment_detail.html', {
        'appointment': appointment,
        'today_date': today_date
    })

@login_required
def appointment_create(request):
    user = request.user
    
    # Vérification préalable pour les étudiants sans heures restantes
    if user.user_type == 'student' and user.student_profile.remaining_hours <= 0:
        messages.error(request, "Vous n'avez plus d'heures disponibles. Veuillez contacter la secrétaire pour acheter un forfait.")
        return redirect('appointment_list')
    
    if request.method == 'POST':
        # Récupération des données du formulaire
        student_id = request.POST.get('student')
        instructor_id = request.POST.get('instructor')
        date_str = request.POST.get('date')
        start_time_str = request.POST.get('start_time')
        duration = int(request.POST.get('duration', 2))
        location = request.POST.get('location')
        notes = request.POST.get('notes')
        
        # Validation des données
        errors = []
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            
            # Calculer l'heure de fin
            start_datetime = datetime.combine(date, start_time)
            end_datetime = start_datetime + timedelta(hours=duration)
            end_time = end_datetime.time()
            
            # Vérifier si la date est dans le futur
            if date < timezone.now().date():
                errors.append("La date du rendez-vous doit être dans le futur.")
                
            # Récupérer l'étudiant et l'instructeur
            if user.user_type == 'student':
                student = user.student_profile
            else:
                student = get_object_or_404(Student, pk=student_id)
                
            if user.user_type == 'instructor':
                instructor = user.instructor_profile
            else:
                instructor = get_object_or_404(Instructor, pk=instructor_id)
                
            # Vérifier si l'étudiant a suffisamment d'heures
            if student.remaining_hours < duration:
                errors.append(f"L'élève n'a pas assez d'heures disponibles ({student.remaining_hours} heures restantes).")
                
            # Vérifier les disponibilités de l'instructeur
            instructor_appointments = Appointment.objects.filter(
                instructor=instructor, 
                date=date,
            ).exclude(pk=pk if 'pk' in locals() else None)
            
            for appt in instructor_appointments:
                appt_start = datetime.combine(appt.date, appt.start_time)
                appt_end = datetime.combine(appt.date, appt.end_time)
                new_start = datetime.combine(date, start_time)
                new_end = datetime.combine(date, end_time)
                
                if (new_start < appt_end and new_end > appt_start):
                    errors.append(f"L'instructeur a déjà un rendez-vous prévu dans cette plage horaire.")
                    break
                    
            # Vérifier les disponibilités de l'étudiant
            student_appointments = Appointment.objects.filter(
                student=student, 
                date=date,
            ).exclude(pk=pk if 'pk' in locals() else None)
            
            for appt in student_appointments:
                appt_start = datetime.combine(appt.date, appt.start_time)
                appt_end = datetime.combine(appt.date, appt.end_time)
                new_start = datetime.combine(date, start_time)
                new_end = datetime.combine(date, end_time)
                
                if (new_start < appt_end and new_end > appt_start):
                    errors.append(f"L'élève a déjà un rendez-vous prévu dans cette plage horaire.")
                    break
                    
        except ValueError as e:
            errors.append(f"Erreur de format de date ou d'heure : {str(e)}")
        
        # S'il y a des erreurs, les afficher
        if errors:
            for error in errors:
                messages.error(request, error)
                
            # Récupérer les listes pour le formulaire
            students = Student.objects.all()
            instructors = Instructor.objects.all()
            
            return render(request, 'scheduling/appointment_form.html', {
                'students': students,
                'instructors': instructors,
                'form_data': request.POST
            })
        
        # Sinon, créer le rendez-vous
        appointment = Appointment(
            student=student,
            instructor=instructor,
            date=date,
            start_time=start_time,
            end_time=end_time,
            location=location,
            duration=duration,
            notes=notes
        )
        appointment.save()
        
        # Déduire les heures du forfait de l'étudiant
        student.remaining_hours -= duration
        student.save()
        
        messages.success(request, "Le rendez-vous a été créé avec succès.")
        return redirect('appointment_detail', pk=appointment.pk)
    
    # Préparer le formulaire
    students = Student.objects.all()
    instructors = Instructor.objects.all()
    
    # Pré-remplir la date si elle est fournie dans l'URL
    initial_date = request.GET.get('date', None)
    
    # Pré-remplir l'instructeur ou l'étudiant si fourni dans l'URL
    initial_instructor = request.GET.get('instructor', None)
    initial_student = request.GET.get('student', None)
    
    return render(request, 'scheduling/appointment_form.html', {
        'students': students,
        'instructors': instructors,
        'initial_date': initial_date,
        'initial_instructor': initial_instructor,
        'initial_student': initial_student
    })

@login_required
def appointment_edit(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    
    # Vérification des permissions
    user = request.user
    if user.user_type not in ['instructor', 'secretary', 'admin']:
        messages.error(request, "Vous n'avez pas l'autorisation de modifier ce rendez-vous.")
        return redirect('appointment_list')
    elif user.user_type == 'instructor' and appointment.instructor.user != user:
        messages.error(request, "Vous ne pouvez modifier que vos propres rendez-vous.")
        return redirect('appointment_list')
    
    # Stocker la durée précédente pour ajuster les heures restantes
    previous_duration = appointment.duration
    
    if request.method == 'POST':
        # Récupération des données du formulaire
        student_id = request.POST.get('student', appointment.student.id)
        instructor_id = request.POST.get('instructor', appointment.instructor.id)
        date_str = request.POST.get('date')
        start_time_str = request.POST.get('start_time')
        duration = int(request.POST.get('duration', appointment.duration))
        location = request.POST.get('location')
        notes = request.POST.get('notes')
        
        # Validation similaire à la création
        # ...
        
        # Mettre à jour le rendez-vous
        appointment.student = get_object_or_404(Student, pk=student_id)
        appointment.instructor = get_object_or_404(Instructor, pk=instructor_id)
        appointment.date = datetime.strptime(date_str, '%Y-%m-%d').date()
        appointment.start_time = datetime.strptime(start_time_str, '%H:%M').time()
        
        # Calculer l'heure de fin
        start_datetime = datetime.combine(appointment.date, appointment.start_time)
        end_datetime = start_datetime + timedelta(hours=duration)
        appointment.end_time = end_datetime.time()
        
        appointment.location = location
        appointment.duration = duration
        appointment.notes = notes
        appointment.save()
        
        # Ajuster les heures restantes de l'étudiant
        student = appointment.student
        if duration != previous_duration:
            adjustment = previous_duration - duration
            student.remaining_hours += adjustment
            student.save()
        
        messages.success(request, "Le rendez-vous a été modifié avec succès.")
        return redirect('appointment_detail', pk=appointment.pk)
    
    # Préparer le formulaire pour l'édition
    students = Student.objects.all()
    instructors = Instructor.objects.all()
    
    return render(request, 'scheduling/appointment_form.html', {
        'appointment': appointment,
        'students': students,
        'instructors': instructors
    })

@login_required
def appointment_delete(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    
    # Vérification des permissions
    user = request.user
    if user.user_type not in ['instructor', 'secretary', 'admin']:
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer ce rendez-vous.")
        return redirect('appointment_list')
    elif user.user_type == 'instructor' and appointment.instructor.user != user:
        messages.error(request, "Vous ne pouvez supprimer que vos propres rendez-vous.")
        return redirect('appointment_list')
    
    if request.method == 'POST':
        # Rendre les heures à l'étudiant
        student = appointment.student
        student.remaining_hours += appointment.duration
        student.save()
        
        # Supprimer le rendez-vous
        appointment.delete()
        
        messages.success(request, "Le rendez-vous a été supprimé avec succès.")
        return redirect('appointment_list')
    
    return render(request, 'scheduling/appointment_confirm_delete.html', {
        'appointment': appointment
    })

@login_required
def calendar_view(request):
    user = request.user
    today = timezone.now().date()
    
    # Déterminer la période à afficher
    week_str = request.GET.get('week', None)
    if week_str:
        try:
            week_date = datetime.strptime(week_str, '%Y-%m-%d').date()
            # S'assurer que c'est un lundi
            start_of_week = week_date - timedelta(days=week_date.weekday())
        except ValueError:
            start_of_week = today - timedelta(days=today.weekday())
    else:
        # Par défaut, utiliser la semaine en cours
        start_of_week = today - timedelta(days=today.weekday())
    
    end_of_week = start_of_week + timedelta(days=6)
    prev_week = start_of_week - timedelta(days=7)
    next_week = start_of_week + timedelta(days=7)
    
    # Filtrer les rendez-vous en fonction du type d'utilisateur
    if user.user_type == 'student':
        appointments = Appointment.objects.filter(
            student=user.student_profile,
            date__range=[start_of_week, end_of_week]
        )
    elif user.user_type == 'instructor':
        appointments = Appointment.objects.filter(
            instructor=user.instructor_profile,
            date__range=[start_of_week, end_of_week]
        )
    else:  # secretary or admin
        # Filtre optionnel par instructeur
        instructor_id = request.GET.get('instructor', None)
        if instructor_id:
            appointments = Appointment.objects.filter(
                instructor_id=instructor_id,
                date__range=[start_of_week, end_of_week]
            )
        else:
            appointments = Appointment.objects.filter(
                date__range=[start_of_week, end_of_week]
            )
    
    # Préparer les données pour l'affichage du calendrier
    calendar_days = []
    for day_offset in range(7):  # Lundi à Dimanche
        current_date = start_of_week + timedelta(days=day_offset)
        is_today = current_date == today
        is_outside_month = current_date.month != today.month
        
        day_events = []
        for appointment in appointments.filter(date=current_date):
            event_type = "student" if user.user_type == 'instructor' else "instructor"
            day_events.append({
                'id': appointment.id,
                'time': f"{appointment.start_time.strftime('%H:%M')} - {appointment.end_time.strftime('%H:%M')}",
                'type': event_type,
                'title': f"{appointment.location} - {appointment.duration}h",
                'student_name': f"{appointment.student.user.first_name} {appointment.student.user.last_name}" if user.user_type != 'student' else f"{appointment.instructor.user.first_name} {appointment.instructor.user.last_name}"
            })
        
        calendar_days.append({
            'date': current_date,
            'is_today': is_today,
            'is_outside_month': is_outside_month,
            'events': day_events
        })
    
    return render(request, 'scheduling/calendar.html', {
        'calendar_days': calendar_days,
        'start_date': start_of_week,
        'end_date': end_of_week,
        'prev_week': prev_week,
        'next_week': next_week,
        'today': today
    })