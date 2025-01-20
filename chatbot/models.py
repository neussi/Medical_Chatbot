from django.db import models
import json


class Symptom(models.Model):
    name_fr = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    description_fr = models.TextField()
    description_en = models.TextField()
    keywords_fr = models.TextField(blank=True) 
    keywords_en = models.TextField(blank=True) 

    def __str__(self):
        return self.name_fr

class Disease(models.Model):
    name_fr = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    description_fr = models.TextField()
    description_en = models.TextField()
    symptoms = models.ManyToManyField(Symptom, related_name='diseases')
    severity = models.IntegerField(choices=[
        (1, 'Légère'),
        (2, 'Modérée'),
        (3, 'Sévère'),
        (4, 'Critique')
    ])

    def __str__(self):
        return self.name_fr


class Hospital(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    phone = models.CharField(max_length=20)
    specialties = models.TextField()  
    emergency = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Doctor(models.Model):
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    languages = models.CharField(max_length=200)  
    available = models.BooleanField(default=True)

    def __str__(self):
        return f"Dr. {self.name} ({self.specialty})"



class Patient(models.Model):
    phone_number = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100, blank=True)
    language = models.CharField(max_length=2, default='fr')
    age = models.IntegerField(null=True)
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')], null=True)
    location_latitude = models.FloatField(null=True)
    location_longitude = models.FloatField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    conversation_state = models.CharField(max_length=50, default='initial')
    current_symptoms = models.TextField(default='')

    # Nouveaux champs pour la gestion de la conversation
    current_disease = models.TextField(blank=True, null=True)  # Stocker la maladie actuelle
    current_medecins = models.TextField(blank=True, null=True)  # Stocker les médecins sous forme de JSON
    current_hospital = models.TextField(blank=True, null=True)  # Stocker l'hôpital sous forme de JSON

    def __str__(self):
        return f"{self.name} ({self.phone_number})"

    # Méthodes pour gérer les données JSON
    def set_current_medecins(self, medecins):
        """Convertit la liste des médecins en JSON et la stocke."""
        self.current_medecins = json.dumps(medecins)

    def get_current_medecins(self):
        """Convertit le JSON des médecins en liste Python."""
        return json.loads(self.current_medecins) if self.current_medecins else []

    def set_current_hospital(self, hospital):
        """Convertit l'hôpital en JSON et le stocke."""
        self.current_hospital = json.dumps(hospital)

    def get_current_hospital(self):
        """Convertit le JSON de l'hôpital en dictionnaire Python."""
        return json.loads(self.current_hospital) if self.current_hospital else {}




class Consultation(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    disease = models.ForeignKey(Disease, on_delete=models.SET_NULL, null=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Consultation for {self.patient} on {self.created_at}"
