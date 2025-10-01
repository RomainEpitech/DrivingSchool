from django import forms
from scheduling.models import Appointment
from accounts.models import Student, Instructor

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['student', 'instructor', 'date', 'start_time', 'duration', 'location', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and user.user_type == 'student':
            self.fields['student'].widget = forms.HiddenInput()
            self.fields['student'].initial = user.student_profile.id
        elif user and user.user_type == 'instructor':
            self.fields['instructor'].widget = forms.HiddenInput()
            self.fields['instructor'].initial = user.instructor_profile.id
    
    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get('student')
        duration = cleaned_data.get('duration')
        
        # Vérifier si l'élève a suffisamment d'heures
        if student and duration:
            if student.remaining_hours < duration:
                raise forms.ValidationError(
                    f"L'élève n'a pas assez d'heures disponibles ({student.remaining_hours} heures restantes)."
                )
        
        return cleaned_data