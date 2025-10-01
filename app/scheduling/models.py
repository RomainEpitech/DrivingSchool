from django.db import models
from accounts.models import Student, Instructor

class Appointment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='appointments')
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=255)
    duration = models.PositiveIntegerField(help_text="Durée en heures")
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['date', 'start_time']
        
    def __str__(self):
        return f"RDV: {self.student} avec {self.instructor} le {self.date} à {self.start_time}"