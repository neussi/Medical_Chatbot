import random

from django.utils import timezone

from chatbot.models import (Consultation, Disease, Doctor, Hospital, Patient,
                            Symptom)

print("Le script generate_data.py a démarré.")

# Liste des maladies courantes au Cameroun
DISEASES = [
    {
        "name_fr": "Paludisme",
        "name_en": "Malaria",
        "description_fr": "Maladie transmise par les moustiques, causant fièvre, frissons et fatigue.",
        "description_en": "Disease transmitted by mosquitoes, causing fever, chills, and fatigue.",
        "severity": 3,
        "symptoms_fr": ["Fièvre", "Frissons", "Fatigue", "Maux de tête"],
        "symptoms_en": ["Fever", "Chills", "Fatigue", "Headache"],
    },
    {
        "name_fr": "Typhoïde",
        "name_en": "Typhoid",
        "description_fr": "Infection bactérienne causant fièvre, maux de tête et douleurs abdominales.",
        "description_en": "Bacterial infection causing fever, headache, and abdominal pain.",
        "severity": 3,
        "symptoms_fr": ["Fièvre", "Douleurs abdominales", "Diarrhée"],
        "symptoms_en": ["Fever", "Abdominal pain", "Diarrhea"],
    },
    {
        "name_fr": "Choléra",
        "name_en": "Cholera",
        "description_fr": "Infection intestinale aiguë causant diarrhée et déshydratation sévère.",
        "description_en": "Acute intestinal infection causing diarrhea and severe dehydration.",
        "severity": 4,
        "symptoms_fr": ["Diarrhée", "Vomissements", "Déshydratation"],
        "symptoms_en": ["Diarrhea", "Vomiting", "Dehydration"],
    },
    {
        "name_fr": "Hypertension",
        "name_en": "Hypertension",
        "description_fr": "Pression artérielle élevée, souvent asymptomatique mais dangereuse.",
        "description_en": "High blood pressure, often asymptomatic but dangerous.",
        "severity": 2,
        "symptoms_fr": ["Maux de tête", "Vertiges", "Fatigue"],
        "symptoms_en": ["Headache", "Dizziness", "Fatigue"],
    },
    {
        "name_fr": "Diabète",
        "name_en": "Diabetes",
        "description_fr": "Trouble métabolique causant une glycémie élevée.",
        "description_en": "Metabolic disorder causing high blood sugar.",
        "severity": 2,
        "symptoms_fr": ["Fatigue", "Soif excessive", "Mictions fréquentes"],
        "symptoms_en": ["Fatigue", "Excessive thirst", "Frequent urination"],
    },
    {
        "name_fr": "VIH/SIDA",
        "name_en": "HIV/AIDS",
        "description_fr": "Maladie virale affectant le système immunitaire.",
        "description_en": "Viral disease affecting the immune system.",
        "severity": 4,
        "symptoms_fr": ["Fatigue", "Fièvre", "Éruptions cutanées"],
        "symptoms_en": ["Fatigue", "Fever", "Skin rashes"],
    },
    {
        "name_fr": "Tuberculose",
        "name_en": "Tuberculosis",
        "description_fr": "Infection bactérienne affectant principalement les poumons.",
        "description_en": "Bacterial infection primarily affecting the lungs.",
        "severity": 4,
        "symptoms_fr": ["Toux persistante", "Fièvre", "Perte de poids"],
        "symptoms_en": ["Persistent cough", "Fever", "Weight loss"],
    },
    {
        "name_fr": "Anémie",
        "name_en": "Anemia",
        "description_fr": "Déficit en globules rouges ou en hémoglobine.",
        "description_en": "Deficiency of red blood cells or hemoglobin.",
        "severity": 2,
        "symptoms_fr": ["Fatigue", "Pâleur", "Essoufflement"],
        "symptoms_en": ["Fatigue", "Pale skin", "Shortness of breath"],
    },
    {
        "name_fr": "Grippe",
        "name_en": "Flu",
        "description_fr": "Infection virale causant fièvre, toux et fatigue.",
        "description_en": "Viral infection causing fever, cough, and fatigue.",
        "severity": 2,
        "symptoms_fr": ["Fièvre", "Toux", "Fatigue", "Douleurs musculaires"],
        "symptoms_en": ["Fever", "Cough", "Fatigue", "Muscle pain"],
    },
    {
        "name_fr": "Dengue",
        "name_en": "Dengue",
        "description_fr": "Maladie virale transmise par les moustiques, causant fièvre et douleurs articulaires.",
        "description_en": "Viral disease transmitted by mosquitoes, causing fever and joint pain.",
        "severity": 3,
        "symptoms_fr": ["Fièvre", "Douleurs articulaires", "Éruptions cutanées"],
        "symptoms_en": ["Fever", "Joint pain", "Skin rashes"],
    },
]

# Liste des symptômes courants
SYMPTOMS = [
    {
        "name_fr": "Fièvre",
        "name_en": "Fever",
        "description_fr": "Augmentation de la température corporelle.",
        "description_en": "Increase in body temperature.",
        "keywords_fr": "fièvre, chaud, température",
        "keywords_en": "fever, hot, temperature",
    },
    {
        "name_fr": "Maux de tête",
        "name_en": "Headache",
        "description_fr": "Douleur localisée au niveau de la tête.",
        "description_en": "Pain localized in the head.",
        "keywords_fr": "maux de tête, migraine, douleur tête",
        "keywords_en": "headache, migraine, head pain",
    },
    {
        "name_fr": "Diarrhée",
        "name_en": "Diarrhea",
        "description_fr": "Selles liquides et fréquentes.",
        "description_en": "Loose and frequent stools.",
        "keywords_fr": "diarrhée, selles liquides",
        "keywords_en": "diarrhea, loose stools",
    },
    {
        "name_fr": "Douleurs abdominales",
        "name_en": "Abdominal pain",
        "description_fr": "Douleur située dans la région de l'abdomen.",
        "description_en": "Pain located in the abdominal region.",
        "keywords_fr": "douleur ventre, mal au ventre, douleur abdominale",
        "keywords_en": "stomach pain, belly ache, abdominal pain",
    },
    {
        "name_fr": "Fatigue",
        "name_en": "Fatigue",
        "description_fr": "Sensation de grande fatigue et manque d'énergie.",
        "description_en": "Feeling of extreme tiredness and lack of energy.",
        "keywords_fr": "fatigue, épuisement, manque d'énergie",
        "keywords_en": "fatigue, exhaustion, lack of energy",
    },
    {
        "name_fr": "Toux",
        "name_en": "Cough",
        "description_fr": "Expulsion brutale d'air des poumons.",
        "description_en": "Sudden expulsion of air from the lungs.",
        "keywords_fr": "toux, toux sèche, toux grasse",
        "keywords_en": "cough, dry cough, wet cough",
    },
    {
        "name_fr": "Douleurs articulaires",
        "name_en": "Joint pain",
        "description_fr": "Douleur localisée au niveau des articulations.",
        "description_en": "Pain localized in the joints.",
        "keywords_fr": "douleur articulaire, mal aux articulations",
        "keywords_en": "joint pain, arthritis",
    },
    {
        "name_fr": "Nausées",
        "name_en": "Nausea",
        "description_fr": "Sensation de malaise et envie de vomir.",
        "description_en": "Feeling of discomfort and urge to vomit.",
        "keywords_fr": "nausées, envie de vomir",
        "keywords_en": "nausea, urge to vomit",
    },
    {
        "name_fr": "Vomissements",
        "name_en": "Vomiting",
        "description_fr": "Rejet du contenu de l'estomac par la bouche.",
        "description_en": "Expulsion of stomach contents through the mouth.",
        "keywords_fr": "vomissements, vomir",
        "keywords_en": "vomiting, throw up",
    },
    {
        "name_fr": "Éruptions cutanées",
        "name_en": "Skin rashes",
        "description_fr": "Apparition de rougeurs ou de boutons sur la peau.",
        "description_en": "Appearance of redness or bumps on the skin.",
        "keywords_fr": "éruption cutanée, rougeurs, boutons",
        "keywords_en": "skin rash, redness, bumps",
    },
]

# Liste des hôpitaux au Cameroun
HOSPITALS = [
    {
        "name": "Hôpital Central de Yaoundé",
        "address": "Yaoundé, Cameroun",
        "latitude": 3.8480,
        "longitude": 11.5021,
        "phone": "+237 222 22 22 22",
        "specialties": "Médecine générale, Urgences, Chirurgie",
        "emergency": True,
    },
    {
        "name": "Hôpital Général de Douala",
        "address": "Douala, Cameroun",
        "latitude": 4.0511,
        "longitude": 9.7679,
        "phone": "+237 233 33 33 33",
        "specialties": "Cardiologie, Pédiatrie, Gynécologie",
        "emergency": True,
    },
    {
        "name": "Clinique de l'Espoir",
        "address": "Bafoussam, Cameroun",
        "latitude": 5.4799,
        "longitude": 10.4176,
        "phone": "+237 244 44 44 44",
        "specialties": "Médecine interne, Dermatologie",
        "emergency": False,
    },
    {
        "name": "Hôpital Laquintinie",
        "address": "Douala, Cameroun",
        "latitude": 4.0600,
        "longitude": 9.7500,
        "phone": "+237 233 44 44 44",
        "specialties": "Chirurgie, Orthopédie, Urologie",
        "emergency": True,
    },
    {
        "name": "Hôpital Régional de Bamenda",
        "address": "Bamenda, Cameroun",
        "latitude": 5.9597,
        "longitude": 10.1457,
        "phone": "+237 233 55 55 55",
        "specialties": "Médecine générale, Pédiatrie",
        "emergency": True,
    },
]

# Liste des médecins
DOCTORS = [
    {
        "name": "Dr. Jean Dupont",
        "specialty": "Médecin généraliste",
        "hospital": "Hôpital Central de Yaoundé",
        "phone": "+237 677 77 77 77",
        "languages": "Français, Anglais",
        "available": True,
    },
    {
        "name": "Dr. Marie Ngo",
        "specialty": "Cardiologue",
        "hospital": "Hôpital Général de Douala",
        "phone": "+237 699 99 99 99",
        "languages": "Français, Anglais",
        "available": True,
    },
    {
        "name": "Dr. Paul Mbakop",
        "specialty": "Pédiatre",
        "hospital": "Clinique de l'Espoir",
        "phone": "+237 655 55 55 55",
        "languages": "Français",
        "available": True,
    },
    {
        "name": "Dr. Alice Tchoupa",
        "specialty": "Dermatologue",
        "hospital": "Hôpital Laquintinie",
        "phone": "+237 677 88 88 88",
        "languages": "Français, Anglais",
        "available": True,
    },
    {
        "name": "Dr. Samuel Ngoula",
        "specialty": "Chirurgien",
        "hospital": "Hôpital Régional de Bamenda",
        "phone": "+237 677 99 99 99",
        "languages": "Français",
        "available": True,
    },
]

# Liste des patients
PATIENTS = [
    {
        "phone_number": "+237 677 11 11 11",
        "name": "Alice Mboua",
        "language": "fr",
        "age": 28,
        "gender": "F",
        "location_latitude": 3.8480,
        "location_longitude": 11.5021,
    },
    {
        "phone_number": "+237 677 22 22 22",
        "name": "Jean Kamga",
        "language": "fr",
        "age": 35,
        "gender": "M",
        "location_latitude": 4.0511,
        "location_longitude": 9.7679,
    },
    {
        "phone_number": "+237 677 33 33 33",
        "name": "Sophie Ndi",
        "language": "en",
        "age": 42,
        "gender": "F",
        "location_latitude": 5.4799,
        "location_longitude": 10.4176,
    },
    {
        "phone_number": "+237 677 44 44 44",
        "name": "Pierre Tchoupo",
        "language": "fr",
        "age": 50,
        "gender": "M",
        "location_latitude": 4.0600,
        "location_longitude": 9.7500,
    },
    {
        "phone_number": "+237 677 55 55 55",
        "name": "Esther Nkeng",
        "language": "en",
        "age": 25,
        "gender": "F",
        "location_latitude": 5.9597,
        "location_longitude": 10.1457,
    },
]

def create_symptoms():
    """Crée les symptômes dans la base de données."""
    for symptom_data in SYMPTOMS:
        symptom, created = Symptom.objects.get_or_create(
            name_fr=symptom_data["name_fr"],
            defaults={
                "name_en": symptom_data["name_en"],
                "description_fr": symptom_data["description_fr"],
                "description_en": symptom_data["description_en"],
                "keywords_fr": symptom_data["keywords_fr"],
                "keywords_en": symptom_data["keywords_en"],
            }
        )
        if created:
            print(f"Création du symptôme : {symptom.name_fr}")
        else:
            print(f"Symptôme déjà existant : {symptom.name_fr}")



def create_hospitals():
    """Crée les hôpitaux dans la base de données."""
    for hospital_data in HOSPITALS:
        hospital, created = Hospital.objects.get_or_create(
            name=hospital_data["name"],
            defaults={
                "address": hospital_data["address"],
                "latitude": hospital_data["latitude"],
                "longitude": hospital_data["longitude"],
                "phone": hospital_data["phone"],
                "specialties": hospital_data["specialties"],
                "emergency": hospital_data["emergency"],
            }
        )
        if created:
            print(f"Création de l'hôpital : {hospital.name}")
        else:
            print(f"Hôpital déjà existant : {hospital.name}")

def create_doctors():
    """Crée les médecins dans la base de données."""
    for doctor_data in DOCTORS:
        hospital = Hospital.objects.get(name=doctor_data["hospital"])
        doctor, created = Doctor.objects.get_or_create(
            name=doctor_data["name"],
            defaults={
                "specialty": doctor_data["specialty"],
                "hospital": hospital,
                "phone": doctor_data["phone"],
                "languages": doctor_data["languages"],
                "available": doctor_data["available"],
            }
        )
        if created:
            print(f"Création du médecin : {doctor.name}")
        else:
            print(f"Médecin déjà existant : {doctor.name}")

def create_patients():
    """Crée les patients dans la base de données."""
    for patient_data in PATIENTS:
        patient, created = Patient.objects.get_or_create(
            phone_number=patient_data["phone_number"],
            defaults={
                "name": patient_data["name"],
                "language": patient_data["language"],
                "age": patient_data["age"],
                "gender": patient_data["gender"],
                "location_latitude": patient_data["location_latitude"],
                "location_longitude": patient_data["location_longitude"],
            }
        )
        if created:
            print(f"Création du patient : {patient.name}")
        else:
            print(f"Patient déjà existant : {patient.name}")

def create_consultations():
    """Crée des consultations dans la base de données."""
    patients = Patient.objects.all()
    diseases = Disease.objects.all()
    doctors = Doctor.objects.all()

    for patient in patients:
        disease = random.choice(diseases)
        doctor = random.choice(doctors)
        consultation, created = Consultation.objects.get_or_create(
            patient=patient,
            disease=disease,
            doctor=doctor,
            defaults={
                "hospital": doctor.hospital,
                "notes": "Consultation de routine.",
                "severity": random.randint(1, 4),
            }
        )
        if created:
            # Associer les symptômes de la maladie à la consultation
            consultation.symptoms.set(disease.symptoms.all())
            print(f"Création de la consultation pour {patient.name} avec la maladie {disease.name_fr}")
        else:
            print(f"Consultation déjà existante pour {patient.name}")

def create_diseases():
    """Crée les maladies dans la base de données."""
    for disease_data in DISEASES:
        # Vérifier si la maladie existe déjà
        if Disease.objects.filter(name_fr=disease_data["name_fr"]).exists():
            print(f"Maladie déjà existante : {disease_data['name_fr']}")
            continue

        disease = Disease.objects.create(
            name_fr=disease_data["name_fr"],
            name_en=disease_data["name_en"],
            description_fr=disease_data["description_fr"],
            description_en=disease_data["description_en"],
            severity=disease_data["severity"],
        )
        print(f"Création de la maladie : {disease.name_fr}")
        # Associer les symptômes à la maladie
        for symptom_name in disease_data["symptoms_fr"]:
            try:
                symptom = Symptom.objects.get(name_fr=symptom_name)
                disease.symptoms.add(symptom)
            except Symptom.DoesNotExist:
                print(f"Erreur : Le symptôme '{symptom_name}' n'existe pas dans la base de données.")
        print(f"Symptômes associés à {disease.name_fr} : {disease_data['symptoms_fr']}")

def run():
    """Exécute la création des données."""
    print("Démarrage du script generate_data.py...")
    create_symptoms()  # Créer les symptômes en premier
    create_diseases()  # Créer les maladies et associer les symptômes
    create_hospitals()
    create_doctors()
    create_patients()
    create_consultations()
    print("Données générées avec succès !")

# Exécuter le script
if __name__ == "__main__":
    run()

# Exécuter le script
if __name__ == "__main__":
    run()
