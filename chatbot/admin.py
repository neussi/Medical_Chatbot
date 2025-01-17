from django.contrib import admin
from .models import Disease, Symptom, Hospital, Doctor, Patient, Consultation

@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ('name_fr', 'name_en', 'severity')
    list_filter = ('severity',)
    search_fields = ('name_fr', 'name_en', 'description_fr', 'description_en')
    filter_horizontal = ('symptoms',)

@admin.register(Symptom)
class SymptomAdmin(admin.ModelAdmin):
    list_display = ('name_fr', 'name_en')
    search_fields = ('name_fr', 'name_en', 'description_fr', 'description_en', 'keywords_fr', 'keywords_en')

@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'emergency')
    list_filter = ('emergency',)
    search_fields = ('name', 'address', 'specialties')

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialty', 'hospital', 'phone', 'available')
    list_filter = ('specialty', 'available', 'hospital')
    search_fields = ('name', 'specialty', 'languages')

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'language', 'age', 'gender', 'created_at', 'conversation_state')
    list_filter = ('language', 'gender', 'conversation_state')
    search_fields = ('name', 'phone_number', 'current_symptoms')

@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'hospital', 'created_at', 'severity')
    list_filter = ('severity', 'created_at')
    search_fields = ('patient__name', 'doctor__name', 'notes')
    filter_horizontal = ('symptoms',)
