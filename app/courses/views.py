from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from courses.models import CoursePackage, Purchase
from accounts.models import Student
from courses.forms import PurchaseForm, CoursePackageForm
from django.utils import timezone
from django.db import models

@login_required
def package_list(request):
    packages = CoursePackage.objects.all()
    return render(request, 'courses/package_list.html', {'packages': packages})

@login_required
def package_detail(request, pk):
    package = get_object_or_404(CoursePackage, pk=pk)
    return render(request, 'courses/package_detail.html', {'package': package})

@login_required
def purchase_package(request, package_id):
    # Seuls les secrétaires et admins peuvent enregistrer des achats
    if request.user.user_type not in ['secretary', 'admin']:
        messages.error(request, "Vous n'avez pas l'autorisation d'effectuer cette action.")
        return redirect('package_list')
    
    package = get_object_or_404(CoursePackage, pk=package_id)
    
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        amount_paid = request.POST.get('amount_paid')
        
        if not student_id:
            messages.error(request, "Veuillez sélectionner un élève.")
            students = Student.objects.all()
            return render(request, 'courses/purchase_form.html', {
                'package': package,
                'students': students
            })
        
        try:
            amount_paid = float(amount_paid)
        except ValueError:
            messages.error(request, "Le montant payé doit être un nombre valide.")
            students = Student.objects.all()
            return render(request, 'courses/purchase_form.html', {
                'package': package,
                'students': students
            })
            
        student = get_object_or_404(Student, pk=student_id)
        
        purchase = Purchase(
            student=student,
            package=package,
            hours_added=package.hours,
            amount_paid=amount_paid
        )
        purchase.save()
        
        messages.success(request, f"Achat enregistré avec succès pour {student.user.first_name} {student.user.last_name}.")
        return redirect('purchase_history')
    
    students = Student.objects.all()
    return render(request, 'courses/purchase_form.html', {
        'package': package,
        'students': students
    })

@login_required
def purchase_history(request):
    user = request.user
    
    if user.user_type == 'student':
        purchases = Purchase.objects.filter(student=user.student_profile)
    elif user.user_type in ['secretary', 'admin']:
        purchases = Purchase.objects.all().order_by('-purchase_date')
    else:
        messages.error(request, "Vous n'avez pas l'autorisation de voir cette page.")
        return redirect('profile')
    
    return render(request, 'courses/purchase_history.html', {'purchases': purchases})

@login_required
def package_create(request):
    # Vérifier les autorisations
    if request.user.user_type not in ['admin', 'secretary']:
        messages.error(request, "Vous n'avez pas l'autorisation d'effectuer cette action.")
        return redirect('package_list')
    
    if request.method == 'POST':
        form = CoursePackageForm(request.POST)
        if form.is_valid():
            package = form.save()
            messages.success(request, f"Le forfait {package.name} a été créé avec succès.")
            return redirect('package_list')
    else:
        form = CoursePackageForm()
    
    return render(request, 'courses/package_form.html', {
        'form': form,
        'is_new': True
    })

@login_required
def package_edit(request, pk):
    # Vérifier les autorisations
    if request.user.user_type not in ['admin', 'secretary']:
        messages.error(request, "Vous n'avez pas l'autorisation d'effectuer cette action.")
        return redirect('package_list')
    
    package = get_object_or_404(CoursePackage, pk=pk)
    
    if request.method == 'POST':
        form = CoursePackageForm(request.POST, instance=package)
        if form.is_valid():
            package = form.save()
            messages.success(request, f"Le forfait {package.name} a été mis à jour avec succès.")
            return redirect('package_list')
    else:
        form = CoursePackageForm(instance=package)
    
    return render(request, 'courses/package_form.html', {
        'form': form,
        'package': package,
        'is_new': False
    })

@login_required
def package_delete(request, pk):
    # Vérifier les autorisations
    if request.user.user_type not in ['admin', 'secretary']:
        messages.error(request, "Vous n'avez pas l'autorisation d'effectuer cette action.")
        return redirect('package_list')
    
    package = get_object_or_404(CoursePackage, pk=pk)
    
    # Vérifier si le forfait peut être supprimé
    if Purchase.objects.filter(package=package).exists():
        messages.error(request, f"Le forfait {package.name} ne peut pas être supprimé car il est associé à des achats.")
        return redirect('package_list')
    
    if request.method == 'POST':
        package_name = package.name
        package.delete()
        messages.success(request, f"Le forfait {package_name} a été supprimé avec succès.")
        return redirect('package_list')
    
    return render(request, 'courses/package_confirm_delete.html', {
        'package': package
    })

@login_required
def accounting_dashboard(request):
    # Vérifier les autorisations (réservé aux administrateurs)
    if request.user.user_type != 'admin':
        messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette page.")
        return redirect('home')
    
    # Récupérer toutes les transactions
    all_purchases = Purchase.objects.all().order_by('-purchase_date')
    
    # Calculer les statistiques
    total_revenue = Purchase.objects.aggregate(total=models.Sum('amount_paid'))['total'] or 0
    
    # Revenus du mois en cours
    current_month = timezone.now().month
    current_year = timezone.now().year
    monthly_revenue = Purchase.objects.filter(
        purchase_date__month=current_month,
        purchase_date__year=current_year
    ).aggregate(total=models.Sum('amount_paid'))['total'] or 0
    
    # Nombre de forfaits vendus par type
    package_stats = Purchase.objects.values('package__name').annotate(
        count=models.Count('id'),
        total=models.Sum('amount_paid')
    ).order_by('-count')
    
    # Revenus par mois (pour le graphique)
    months = []
    revenues = []
    
    for i in range(6, 0, -1):
        # Calculer la date pour les 6 derniers mois
        date = timezone.now() - timezone.timedelta(days=30 * i)
        month = date.month
        year = date.year
        
        month_name = date.strftime('%B %Y')
        
        month_revenue = Purchase.objects.filter(
            purchase_date__month=month,
            purchase_date__year=year
        ).aggregate(total=models.Sum('amount_paid'))['total'] or 0
        
        months.append(month_name)
        revenues.append(float(month_revenue))
    
    # Ajouter le mois en cours
    current_month_name = timezone.now().strftime('%B %Y')
    months.append(current_month_name)
    revenues.append(float(monthly_revenue))
    
    context = {
        'all_purchases': all_purchases,
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'package_stats': package_stats,
        'months': months,
        'revenues': revenues,
    }
    
    return render(request, 'courses/accounting_dashboard.html', context)