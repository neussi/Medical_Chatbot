from django.core.management.base import BaseCommand
from chatbot.models import Disease, Symptom, Hospital, Doctor

class Command(BaseCommand):
    help = 'Loads initial medical data into the database'

    def handle(self, *args, **kwargs):
        # Créer les symptômes
        symptoms_data = [
            {
                'name_fr': 'Fièvre',
                'name_en': 'Fever',
                'description_fr': 'Température corporelle élevée',
                'description_en': 'Elevated body temperature',
                'keywords_fr': 'fièvre,chaud,température,chaleur',  
                'keywords_en': 'fever,hot,temperature,heat' 
            },
            {
                'name_fr': 'Toux',
                'name_en': 'Cough',
                'description_fr': 'Toux sèche ou grasse',
                'description_en': 'Dry or wet cough',
                'keywords_fr': 'toux,tousser,crachat',
                'keywords_en': 'cough,coughing,sputum'
            },
            {
                'name_fr': 'Maux de tête',
                'name_en': 'Headache',
                'description_fr': 'Douleur à la tête',
                'description_en': 'Pain in the head',
                'keywords_fr': 'mal de tête,migraine,céphalée',
                'keywords_en': 'headache,migraine,head pain'
            },
            # Ajoutez plus de symptômes ici
        ]

        for symptom_data in symptoms_data:
            Symptom.objects.get_or_create(
                name_fr=symptom_data['name_fr'],
                defaults=symptom_data
            )

        # Créer les maladies
        diseases_data = [
            {
                'name_fr': 'Grippe',
                'name_en': 'Flu',
                'description_fr': 'Infection virale respiratoire',
                'description_en': 'Viral respiratory infection',
                'severity': 2,
                'symptoms': ['Fièvre', 'Toux', 'Maux de tête']
            },
            # Ajoutez plus de maladies ici
        ]

        for disease_data in diseases_data:
            symptoms = disease_data.pop('symptoms')
            disease, _ = Disease.objects.get_or_create(
                name_fr=disease_data['name_fr'],
                defaults=disease_data
            )
            disease.symptoms.set(Symptom.objects.filter(name_fr__in=symptoms))

        # Créer les hôpitaux
        hospitals_data = [
            {
                'name': 'Hôpital Saint-Louis',
                'address': '1 Avenue Claude Vellefaux, 75010 Paris',
                'latitude': 48.8747,
                'longitude': 2.3684,
                'phone': '01 42 49 49 49',
                'specialties': 'Dermatologie,Oncologie',  
                'emergency': True
            },
            # Ajoutez plus d'hôpitaux ici
        ]

        for hospital_data in hospitals_data:
            Hospital.objects.get_or_create(
                name=hospital_data['name'],
                defaults=hospital_data
            )

        # Créer les médecins
        doctors_data = [
            {
                'name': 'Dr. Martin',
                'specialty': 'Médecine générale',
                'hospital': 'Hôpital Saint-Louis',
                'phone': '01 42 49 49 50',
                'languages': 'fr,en',  
                'available': True
            },
            # Ajoutez plus de médecins ici
        ]

        for doctor_data in doctors_data:
            hospital_name = doctor_data.pop('hospital')
            hospital = Hospital.objects.get(name=hospital_name)
            Doctor.objects.get_or_create(
                name=doctor_data['name'],
                hospital=hospital,
                defaults=doctor_data
            )

        self.stdout.write(self.style.SUCCESS('Successfully loaded initial data'))
