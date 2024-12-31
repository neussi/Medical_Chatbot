# chatbot/models.py
from django.db import models

class Patient(models.Model):
    phone_number = models.CharField(max_length=20, unique=True)
    language = models.CharField(max_length=2, default='fr')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.phone_number

class Conversation(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    message = models.TextField()
    is_from_patient = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']

class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    symptoms = models.TextField()
    diagnosis = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Doctor(models.Model):
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)
    available = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name