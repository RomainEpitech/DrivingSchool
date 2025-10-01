from django.db import models
from accounts.models import Student

class CoursePackage(models.Model):
    name = models.CharField(max_length=100)
    hours = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} ({self.hours}h) - {self.price}€"
    
class Purchase(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='purchases')
    package = models.ForeignKey(CoursePackage, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)
    hours_added = models.PositiveIntegerField()
    amount_paid = models.DecimalField(max_digits=8, decimal_places=2)
    
    def __str__(self):
        return f"Achat par {self.student} le {self.purchase_date.strftime('%d/%m/%Y')}"
    
    def save(self, *args, **kwargs):
        # Mettre à jour le nombre d'heures restantes de l'étudiant lors de l'achat
        if not self.pk:  # Seulement lors de la création
            self.student.remaining_hours += self.hours_added
            self.student.save()
        super().save(*args, **kwargs)