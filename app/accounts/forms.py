from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from accounts.models import User, Instructor, Student

class InstructorForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, label="Prénom")
    last_name = forms.CharField(max_length=30, required=True, label="Nom")
    email = forms.EmailField(required=True, label="Email")
    phone_number = forms.CharField(max_length=15, required=True, label="Téléphone")
    address = forms.CharField(widget=forms.Textarea, required=True, label="Adresse")
    username = forms.CharField(max_length=30, required=True, label="Nom d'utilisateur")
    password = forms.CharField(widget=forms.PasswordInput, required=False, label="Mot de passe")
    specialization = forms.CharField(max_length=100, required=True, label="Spécialisation")
    
    class Meta:
        model = Instructor
        fields = ['specialization']
    
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.get('instance', None)
        if self.instance and self.instance.pk:
            kwargs.setdefault('initial', {})
            kwargs['initial'].update({
                'first_name': self.instance.user.first_name,
                'last_name': self.instance.user.last_name,
                'email': self.instance.user.email,
                'phone_number': self.instance.user.phone_number,
                'address': self.instance.user.address,
                'username': self.instance.user.username,
            })
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['password'].required = False
            self.fields['username'].widget.attrs['readonly'] = True
    
    def save(self, commit=True):
        instructor = super().save(commit=False)
        
        if not instructor.pk:
            # Création d'un nouvel instructeur
            user = User.objects.create_user(
                username=self.cleaned_data['username'],
                password=self.cleaned_data['password'],
                email=self.cleaned_data['email'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                user_type='instructor',
                phone_number=self.cleaned_data['phone_number'],
                address=self.cleaned_data['address'],
            )
            instructor.user = user
        else:
            # Mise à jour d'un instructeur existant
            user = instructor.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.phone_number = self.cleaned_data['phone_number']
            user.address = self.cleaned_data['address']
            
            if self.cleaned_data['password']:
                user.set_password(self.cleaned_data['password'])
            user.save()
        
        if commit:
            instructor.save()
        
        return instructor

class StudentForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, label="Prénom")
    last_name = forms.CharField(max_length=30, required=True, label="Nom")
    email = forms.EmailField(required=True, label="Email")
    phone_number = forms.CharField(max_length=15, required=True, label="Téléphone")
    address = forms.CharField(widget=forms.Textarea, required=True, label="Adresse")
    username = forms.CharField(max_length=30, required=True, label="Nom d'utilisateur")
    password = forms.CharField(widget=forms.PasswordInput, required=False, label="Mot de passe")
    remaining_hours = forms.IntegerField(required=False, min_value=0, label="Heures restantes", initial=0)
    
    class Meta:
        model = Student
        fields = ['remaining_hours']
    
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.get('instance', None)
        if self.instance and self.instance.pk:
            kwargs.setdefault('initial', {})
            kwargs['initial'].update({
                'first_name': self.instance.user.first_name,
                'last_name': self.instance.user.last_name,
                'email': self.instance.user.email,
                'phone_number': self.instance.user.phone_number,
                'address': self.instance.user.address,
                'username': self.instance.user.username,
            })
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['password'].required = False
            self.fields['username'].widget.attrs['readonly'] = True
    
    def save(self, commit=True):
        student = super().save(commit=False)
        
        if not student.pk:
            # Création d'un nouvel élève
            user = User.objects.create_user(
                username=self.cleaned_data['username'],
                password=self.cleaned_data['password'],
                email=self.cleaned_data['email'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                user_type='student',
                phone_number=self.cleaned_data['phone_number'],
                address=self.cleaned_data['address'],
            )
            student.user = user
        else:
            # Mise à jour d'un élève existant
            user = student.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.phone_number = self.cleaned_data['phone_number']
            user.address = self.cleaned_data['address']
            
            if self.cleaned_data['password']:
                user.set_password(self.cleaned_data['password'])
            user.save()
        
        if commit:
            student.save()
        
        return student