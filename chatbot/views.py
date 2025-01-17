import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from django.http import HttpResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from twilio.twiml.messaging_response import MessagingResponse

from .models import Consultation, Disease, Doctor, Hospital, Patient, Symptom

# Configuration du logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Constantes pour les langues
LANG_FR = 'fr'
LANG_EN = 'en'

# Messages multi-langue avec emojis
MESSAGES = {
    LANG_FR: {
        'greeting': "👋 Bonjour! Je suis votre assistant santé virtuel. Comment puis-je vous aider aujourd'hui?\n\n"
                   "1️⃣ Nouvelle consultation médicale 🏥\n"
                   "2️⃣ Voir mes consultations précédentes 📋",
        'goodbye': "🙏 Au revoir! Prenez soin de vous. N'hésitez pas à revenir si vous avez besoin d'aide.\n"
                  "Pour une nouvelle consultation, envoyez simplement 'Bonjour'! 👋",
        'ask_symptoms': "🩺 Pour mieux vous aider, décrivez-moi vos symptômes en détail.\n"
                       "Par exemple: 'J'ai de la fièvre, mal à la tête et je tousse'",
        'no_symptoms': "🤔 Je n'ai pas pu identifier vos symptômes. Pouvez-vous les décrire différemment?\n"
                      "Soyez le plus précis possible dans votre description.",
        'symptoms_detected': "✅ J'ai identifié les symptômes suivants:\n{symptoms}\n\n"
                           "Est-ce correct?\n"
                           "1️⃣ Oui\n"
                           "2️⃣ Non, je veux redécrire mes symptômes",
        'disease_found': "🔍 D'après vos symptômes, il pourrait s'agir de : {disease}\n\n"
                        "📝 Description :\n{description}\n\n"
                        "Niveau de gravité : {severity}\n\n"
                        "Que souhaitez-vous faire ?\n"
                        "1️⃣ Consulter un médecin spécialiste 👨‍⚕️\n"
                        "2️⃣ Trouver un hôpital proche 🏥\n"
                        "3️⃣ Terminer la consultation ❌",
        'no_disease': "⚠️ Je n'ai pas pu identifier précisément votre condition.\n"
                     "Par précaution, je vous recommande de:\n\n"
                     "1️⃣ Consulter un médecin généraliste 👨‍⚕️\n"
                     "2️⃣ Vous rendre aux urgences si vos symptômes sont graves 🏥\n"
                     "3️⃣ Terminer la consultation ❌",
        'doctor_found': "👨‍⚕️ J'ai trouvé un médecin spécialiste pour vous :\n\n"
                       "📛 Dr. {name}\n"
                       "🏥 {hospital}\n"
                       "📞 {phone}\n"
                       "🗣️ Langues: {languages}\n\n"
                       "Voulez-vous:\n"
                       "1️⃣ Trouver un hôpital\n"
                       "2️⃣ Terminer la consultation",
        'no_doctor': "😔 Désolé, je n'ai pas trouvé de médecin spécialiste disponible pour le moment.\n"
                    "Je vous conseille de:\n\n"
                    "1️⃣ Chercher un hôpital proche\n"
                    "2️⃣ Terminer la consultation",
        'hospital_found': "🏥 Voici l'hôpital le plus adapté :\n\n"
                        "📍 {name}\n"
                        "🗺️ {address}\n"
                        "📞 {phone}\n"
                        "🚑 Service d'urgence: {emergency}\n\n"
                        "Tapez 'merci' pour terminer la consultation.",
        'no_hospital': "😔 Désolé, je n'ai pas trouvé d'hôpital spécialisé à proximité.\n"
                      "Je vous recommande d'appeler le 15 en cas d'urgence.\n\n"
                      "Tapez 'merci' pour terminer la consultation.",
        'consultation_history': "📋 Historique de vos consultations:\n\n{history}\n\n"
                              "Pour une nouvelle consultation, tapez 'nouvelle consultation'",
        'no_history': "📭 Vous n'avez pas encore de consultation enregistrée.\n\n"
                     "Voulez-vous commencer une nouvelle consultation?\n"
                     "1️⃣ Oui\n"
                     "2️⃣ Non",
        'consultation_saved': "✅ Votre consultation a été enregistrée.\n"
                            "Prenez soin de vous! 💪\n\n"
                            "Pour une nouvelle consultation, envoyez 'Bonjour'",
        'error': "❌ Désolé, une erreur est survenue. Veuillez réessayer en envoyant 'Bonjour'.",
        'invalid_choice': "⚠️ Je n'ai pas compris votre choix.\n"
                         "Veuillez répondre avec le numéro correspondant à votre choix.",
        'severity_levels': {
            1: "⚪ Légère",
            2: "🟡 Modérée",
            3: "🟠 Sévère",
            4: "🔴 Critique"
        }
    },
    LANG_EN: {
        'greeting': "👋 Hello! I'm your virtual health assistant. How can I help you today?\n\n"
                   "1️⃣ New medical consultation 🏥\n"
                   "2️⃣ View my previous consultations 📋",
        'goodbye': "🙏 Goodbye! Take care. Don't hesitate to come back if you need help.\n"
                  "For a new consultation, just send 'Hello'! 👋",
        'ask_symptoms': "🩺 To better help you, please describe your symptoms in detail.\n"
                       "For example: 'I have fever, headache and I'm coughing'",
        'no_symptoms': "🤔 I couldn't identify your symptoms. Can you describe them differently?\n"
                      "Please be as precise as possible in your description.",
        'symptoms_detected': "✅ I identified the following symptoms:\n{symptoms}\n\n"
                           "Is this correct?\n"
                           "1️⃣ Yes\n"
                           "2️⃣ No, I want to describe my symptoms again",
        'disease_found': "🔍 Based on your symptoms, it could be: {disease}\n\n"
                        "📝 Description:\n{description}\n\n"
                        "Severity level: {severity}\n\n"
                        "What would you like to do?\n"
                        "1️⃣ Consult a specialist doctor 👨‍⚕️\n"
                        "2️⃣ Find a nearby hospital 🏥\n"
                        "3️⃣ End consultation ❌",
        'no_disease': "⚠️ I couldn't identify your condition precisely.\n"
                     "As a precaution, I recommend:\n\n"
                     "1️⃣ Consulting a general practitioner 👨‍⚕️\n"
                     "2️⃣ Going to emergency if symptoms are severe 🏥\n"
                     "3️⃣ End consultation ❌",
        'doctor_found': "👨‍⚕️ I found a specialist doctor for you:\n\n"
                       "📛 Dr. {name}\n"
                       "🏥 {hospital}\n"
                       "📞 {phone}\n"
                       "🗣️ Languages: {languages}\n\n"
                       "Would you like to:\n"
                       "1️⃣ Find a hospital\n"
                       "2️⃣ End consultation",
        'no_doctor': "😔 Sorry, I couldn't find an available specialist doctor at the moment.\n"
                    "I recommend:\n\n"
                    "1️⃣ Looking for a nearby hospital\n"
                    "2️⃣ End consultation",
        'hospital_found': "🏥 Here's the most suitable hospital:\n\n"
                        "📍 {name}\n"
                        "🗺️ {address}\n"
                        "📞 {phone}\n"
                        "🚑 Emergency service: {emergency}\n\n"
                        "Type 'thanks' to end the consultation.",
        'no_hospital': "😔 Sorry, I couldn't find a specialized hospital nearby.\n"
                      "Please call emergency services if urgent.\n\n"
                      "Type 'thanks' to end the consultation.",
        'consultation_history': "📋 Your consultation history:\n\n{history}\n\n"
                              "For a new consultation, type 'new consultation'",
        'no_history': "📭 You don't have any recorded consultations yet.\n\n"
                     "Would you like to start a new consultation?\n"
                     "1️⃣ Yes\n"
                     "2️⃣ No",
        'consultation_saved': "✅ Your consultation has been saved.\n"
                            "Take care! 💪\n\n"
                            "For a new consultation, send 'Hello'",
        'error': "❌ Sorry, an error occurred. Please try again by sending 'Hello'.",
        'invalid_choice': "⚠️ I didn't understand your choice.\n"
                         "Please respond with the number corresponding to your choice.",
        'severity_levels': {
            1: "⚪ Mild",
            2: "🟡 Moderate",
            3: "🟠 Severe",
            4: "🔴 Critical"
        }
    }
}


def detect_language(message: str) -> str:
    """Détecte la langue du message."""
    message = message.lower()
    french_greetings = ['bonjour', 'salut', 'bonsoir', 'coucou']
    english_greetings = ['hello', 'hi', 'hey', 'good']
    
    if any(word in message for word in french_greetings):
        return LANG_FR
    elif any(word in message for word in english_greetings):
        return LANG_EN
    return LANG_FR  # Default to French

def is_greeting(message: str) -> bool:
    """Vérifie si le message est une salutation."""
    message = message.lower()
    greetings = ['bonjour', 'salut', 'bonsoir', 'coucou', 'hello', 'hi', 'hey', 'good']
    return any(word in message for word in greetings)

def is_goodbye(message: str) -> bool:
    """Vérifie si le message est un au revoir."""
    message = message.lower()
    goodbyes = ['merci', 'thanks', 'thank', 'ok', 'bye', 'goodbye', 'au revoir']
    return any(word in message for word in goodbyes)

def get_message(key: str, language: str, **kwargs) -> str:
    """Récupère un message traduit avec des paramètres."""
    message = MESSAGES.get(language, MESSAGES[LANG_FR]).get(key, MESSAGES[LANG_FR].get(key, ''))
    return message.format(**kwargs) if kwargs else message

def find_symptoms(text: str, language: str) -> List[Symptom]:
    """Trouve les symptômes correspondants dans le texte."""
    text = text.lower()
    matching_symptoms = []
    
    for symptom in Symptom.objects.all():
        keywords = getattr(symptom, f'keywords_{language}', '').split(',')
        if any(keyword.strip() in text for keyword in keywords):
            matching_symptoms.append(symptom)
    
    return matching_symptoms

def find_best_disease(symptoms: List[Symptom]) -> Tuple[Optional[Disease], float]:
    """Trouve la maladie la plus probable et son score de correspondance."""
    if not symptoms:
        return None, 0.0
    
    diseases = Disease.objects.filter(symptoms__in=symptoms).distinct()
    best_match = None
    best_score = 0.0
    
    for disease in diseases:
        disease_symptoms = set(disease.symptoms.all())
        patient_symptoms = set(symptoms)
        
        # Calcul du score avec pondération par gravité
        common_symptoms = disease_symptoms.intersection(patient_symptoms)
        score = (len(common_symptoms) / len(disease_symptoms)) * (1 + (disease.severity / 10))
        
        if score > best_score:
            best_score = score
            best_match = disease
    
    return best_match, best_score

def find_doctor(disease: Disease, language: str) -> Optional[Doctor]:
    """Trouve un médecin approprié pour la maladie."""
    return Doctor.objects.filter(
        specialty=disease.specialty,
        available=True,
        languages__contains=language
    ).first()

def find_hospital(disease: Disease) -> Optional[Hospital]:
    """Trouve un hôpital approprié pour la maladie."""
    return Hospital.objects.filter(
        specialties__contains=disease.specialty,
    ).first()

def format_consultation_history(patient: Patient, language: str) -> str:
    """Formate l'historique des consultations."""
    consultations = Consultation.objects.filter(patient=patient).order_by('-created_at')[:5]
    
    if not consultations:
        return get_message('no_history', language)
    
    history_items = []
    for cons in consultations:
        disease_name = getattr(cons.disease, f'name_{language}', 'Non diagnostiqué') if cons.disease else 'Non diagnostiqué'
        severity = MESSAGES[language]['severity_levels'].get(cons.severity, '')
        
        symptoms = ', '.join(getattr(s, f'name_{language}') for s in cons.symptoms.all())
        
        history_items.append(
            f"📅 {cons.created_at.strftime('%d/%m/%Y %H:%M')}\n"
            f"🔍 Diagnostic: {disease_name}\n"
            f"⚡ Gravité: {severity}\n"
            f"🩺 Symptômes: {symptoms}\n"
            f"👨‍⚕️ Médecin: {cons.doctor.name if cons.doctor else 'Non assigné'}\n"
            f"🏥 Hôpital: {cons.hospital.name if cons.hospital else 'Non assigné'}\n"
            f"📝 Notes: {cons.notes if cons.notes else 'Aucune note'}\n"
        )
    
    return '\n\n'.join(history_items)

def save_consultation(
    patient: Patient,
    symptoms: List[Symptom],
    disease: Optional[Disease] = None,
    doctor: Optional[Doctor] = None,
    hospital: Optional[Hospital] = None,
    notes: str = ''
) -> Consultation:
    """Enregistre une nouvelle consultation."""
    consultation = Consultation.objects.create(
        patient=patient,
        disease=disease,
        doctor=doctor,
        hospital=hospital,
        notes=notes,
        severity=disease.severity if disease else 1
    )
    consultation.symptoms.set(symptoms)
    return consultation

def handle_conversation_state(patient: Patient, message: str) -> str:
    """Gère l'état de la conversation et renvoie la réponse appropriée."""
    message = message.lower().strip()
    language = patient.language
    state = patient.conversation_state
    
    logger.info(f"Handling message: {message}")
    logger.info(f"Current state: {state}")
    
    try:
        # Détection de la langue et gestion des salutations
        if is_greeting(message):
            patient.language = detect_language(message)
            patient.conversation_state = 'menu_principal'
            patient.save()
            logger.info(f"New state: {patient.conversation_state}")
            return get_message('greeting', patient.language)
        
        # Gestion des au revoir
        if is_goodbye(message):
            # Sauvegarder la consultation si elle était en cours
            if hasattr(patient, 'current_symptoms') and patient.current_symptoms:
                symptoms = [Symptom.objects.get(id=int(s_id)) for s_id in patient.current_symptoms.split(',') if s_id]
                if symptoms:
                    disease = None
                    if hasattr(patient, 'current_disease') and patient.current_disease:
                        disease = Disease.objects.get(id=int(patient.current_disease))
                    save_consultation(patient, symptoms, disease)
            
            patient.conversation_state = 'initial'
            patient.current_symptoms = ''
            patient.current_disease = None
            patient.save()
            logger.info(f"New state: {patient.conversation_state}")
            return get_message('goodbye', language)
        
        # Gestion des différents états de conversation
        if state == 'menu_principal':
            if message in ['1', 'nouvelle consultation', 'new consultation']:
                patient.conversation_state = 'attente_symptomes'
                patient.save()
                logger.info(f"New state: {patient.conversation_state}")
                return get_message('ask_symptoms', language)
            elif message in ['2', 'historique', 'history']:
                return get_message('consultation_history', language, 
                                 history=format_consultation_history(patient, language))
            else:
                # Renvoyer le menu principal au lieu d'un message d'erreur
                return get_message('greeting', language)
        
        elif state == 'attente_symptomes':
            symptoms = find_symptoms(message, language)
            logger.info(f"Detected symptoms: {symptoms}")
            if not symptoms:
                return get_message('no_symptoms', language)
            
            # Stockage temporaire des symptômes
            patient.current_symptoms = ','.join(str(s.id) for s in symptoms)
            patient.conversation_state = 'confirmation_symptomes'
            patient.save()
            logger.info(f"New state: {patient.conversation_state}")
            
            symptoms_text = '\n'.join(f"- {getattr(s, f'name_{language}')}" for s in symptoms)
            return get_message('symptoms_detected', language, symptoms=symptoms_text)
        
        elif state == 'confirmation_symptomes':
            if message == '1':  # Confirmation des symptômes
                symptoms = [Symptom.objects.get(id=int(s_id)) for s_id in patient.current_symptoms.split(',')]
                disease, score = find_best_disease(symptoms)
                logger.info(f"Best match: {disease.name_fr if disease else 'None'} with score {score}")
                
                if disease and score > 0.5:  # Seuil de confiance
                    patient.current_disease = disease.id
                    patient.conversation_state = 'proposition_actions'
                    patient.save()
                    logger.info(f"New state: {patient.conversation_state}")
                    
                    return get_message('disease_found', language,
                                     disease=getattr(disease, f'name_{language}'),
                                     description=getattr(disease, f'description_{language}'),
                                     severity=MESSAGES[language]['severity_levels'][disease.severity])
                else:
                    return get_message('no_disease', language)
            
            elif message == '2':  # Nouvelle saisie des symptômes
                patient.current_symptoms = ''
                patient.conversation_state = 'attente_symptomes'
                patient.save()
                logger.info(f"New state: {patient.conversation_state}")
                return get_message('ask_symptoms', language)
            
            else:
                # Renvoyer le message de confirmation au lieu d'un message d'erreur
                symptoms = [Symptom.objects.get(id=int(s_id)) for s_id in patient.current_symptoms.split(',')]
                symptoms_text = '\n'.join(f"- {getattr(s, f'name_{language}')}" for s in symptoms)
                return get_message('symptoms_detected', language, symptoms=symptoms_text)
        
        elif state == 'proposition_actions':
            disease = Disease.objects.get(id=int(patient.current_disease)) if patient.current_disease else None
            
            if message == '1':  # Recherche médecin
                if disease:
                    doctor = find_doctor(disease, language)
                    if doctor:
                        return get_message('doctor_found', language,
                                         name=doctor.name,
                                         hospital=doctor.hospital.name,
                                         phone=doctor.phone,
                                         languages=doctor.languages)
                return get_message('no_doctor', language)
            
            elif message == '2':  # Recherche hôpital
                if disease:
                    hospital = find_hospital(disease)
                    if hospital:
                        return get_message('hospital_found', language,
                                         name=hospital.name,
                                         address=hospital.address,
                                         phone=hospital.phone,
                                         emergency='✅' if hospital.emergency else '❌')
                return get_message('no_hospital', language)
            
            elif message == '3':  # Fin de consultation
                symptoms = [Symptom.objects.get(id=int(s_id)) for s_id in patient.current_symptoms.split(',')]
                save_consultation(patient, symptoms, disease)
                
                patient.conversation_state = 'initial'
                patient.current_symptoms = ''
                patient.current_disease = None
                patient.save()
                logger.info(f"New state: {patient.conversation_state}")
                
                return get_message('consultation_saved', language)
            
            else:
                # Renvoyer les options au lieu d'un message d'erreur
                return get_message('disease_found', language,
                                 disease=getattr(disease, f'name_{language}'),
                                 description=getattr(disease, f'description_{language}'),
                                 severity=MESSAGES[language]['severity_levels'][disease.severity])
        
    except Exception as e:
        logger.error(f"Error in handle_conversation_state: {str(e)}")
        return get_message('error', language)

@csrf_exempt
@require_http_methods(["GET", "POST"])
def webhook(request):
    """Webhook principal pour la gestion des messages WhatsApp"""
    try:
        # Pour les requêtes GET (vérification du webhook)
        if request.method == 'GET':
            return HttpResponse(json.dumps({
                "status": "active",
                "timestamp": datetime.now().isoformat()
            }), content_type="application/json")

        # Pour les requêtes POST (messages WhatsApp)
        incoming_msg = request.POST.get('Body', '').strip()
        sender_phone = request.POST.get('From', '').replace('whatsapp:', '')
        
        if not sender_phone or not incoming_msg:
            logger.error("Missing message parameters")
            return HttpResponse("Invalid request", status=400)
        
        # Créer ou récupérer le patient
        patient, created = Patient.objects.get_or_create(
            phone_number=sender_phone,
            defaults={
                'language': LANG_FR,
                'conversation_state': 'initial'
            }
        )
        
        # Logger l'état de la conversation
        logger.info(f"Conversation state for {sender_phone}: {patient.conversation_state}")
        logger.info(f"Received message: {incoming_msg}")
        
        # Obtenir la réponse
        try:
            response_text = handle_conversation_state(patient, incoming_msg)
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            response_text = get_message('error', patient.language)
            
        # Créer la réponse Twilio
        resp = MessagingResponse()
        resp.message(response_text)
        
        # Dans la fonction webhook, avant de retourner la réponse
        logger.info(f"Response XML: {str(resp)}")
        return HttpResponse(str(resp), content_type="application/xml")

    except Exception as e:
        logger.error(f"Unexpected error in webhook: {str(e)}")
        return HttpResponse("Internal Server Error", status=500)
