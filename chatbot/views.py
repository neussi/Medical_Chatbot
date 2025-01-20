import json
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional

from django.http import HttpResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from twilio.twiml.messaging_response import MessagingResponse

from .models import Consultation, Disease, Doctor, Hospital, Patient, Symptom

# Configuration du logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# URL de l'API Node.js
NODE_API_URL = "http://localhost:3000/moteurinferenceapi/diagnostic"

# Constantes pour les langues
LANG_FR = 'fr'
LANG_EN = 'en'

# Messages multi-langue avec emojis
MESSAGES = {
    LANG_FR: {
        'greeting': "👋 Bonjour! Je suis votre assistant santé virtuel. Comment puis-je vous aider aujourd'hui?\n\n"
                   "1️⃣ Nouvelle consultation médicale 🏥\n"
                   "2️⃣ Quitter ❌",
        'goodbye': "🙏 Au revoir! Prenez soin de vous. N'hésitez pas à revenir si vous avez besoin d'aide.\n"
                  "Pour une nouvelle consultation, envoyez simplement 'Bonjour'! 👋",
        'ask_symptoms': "🩺 Pour mieux vous aider, décrivez-moi vos symptômes en détail.\n"
                       "Par exemple: 'J'ai de la fièvre, mal à la tête et je tousse'",
        'no_symptoms': "🤔 Je n'ai pas pu identifier vos symptômes. Pouvez-vous les décrire différemment?\n"
                      "Soyez le plus précis possible dans votre description.",
        'disease_found': "🔍 D'après vos symptômes, il pourrait s'agir de : {disease}\n\n"
                        "📝 Description :\n{description}\n\n"
                        "Niveau de gravité : {severity}\n\n"
                        "Que souhaitez-vous faire ?\n"
                        "1️⃣ Consulter un médecin spécialiste 👨‍⚕️\n"
                        "2️⃣ Trouver un hôpital proche 🏥\n"
                        "3️⃣ Terminer la consultation ❌",
        'doctor_found': "👨‍⚕️ J'ai trouvé un médecin spécialiste pour vous :\n\n"
                       "📛 Dr. {name}\n"
                       "🏥 {hospital}\n"
                       "📞 {phone}\n"
                       "🗣️ Langues: {languages}\n\n"
                       "Voulez-vous:\n"
                       "1️⃣ Trouver un hôpital\n"
                       "2️⃣ Terminer la consultation",
        'hospital_found': "🏥 Voici l'hôpital le plus adapté :\n\n"
                        "📍 {name}\n"
                        "🗺️ {address}\n"
                        "📞 {phone}\n"
                        "🚑 Service d'urgence: {emergency}\n\n"
                        "Tapez 'merci' pour terminer la consultation.",
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
                   "2️⃣ Quit ❌",
        'goodbye': "🙏 Goodbye! Take care. Don't hesitate to come back if you need help.\n"
                  "For a new consultation, just send 'Hello'! 👋",
        'ask_symptoms': "🩺 To better help you, please describe your symptoms in detail.\n"
                       "For example: 'I have fever, headache and I'm coughing'",
        'no_symptoms': "🤔 I couldn't identify your symptoms. Can you describe them differently?\n"
                      "Please be as precise as possible in your description.",
        'disease_found': "🔍 Based on your symptoms, it could be: {disease}\n\n"
                        "📝 Description:\n{description}\n\n"
                        "Severity level: {severity}\n\n"
                        "What would you like to do?\n"
                        "1️⃣ Consult a specialist doctor 👨‍⚕️\n"
                        "2️⃣ Find a nearby hospital 🏥\n"
                        "3️⃣ End consultation ❌",
        'doctor_found': "👨‍⚕️ I found a specialist doctor for you:\n\n"
                       "📛 Dr. {name}\n"
                       "🏥 {hospital}\n"
                       "📞 {phone}\n"
                       "🗣️ Languages: {languages}\n\n"
                       "Would you like to:\n"
                       "1️⃣ Find a hospital\n"
                       "2️⃣ End consultation",
        'hospital_found': "🏥 Here's the most suitable hospital:\n\n"
                        "📍 {name}\n"
                        "🗺️ {address}\n"
                        "📞 {phone}\n"
                        "🚑 Emergency service: {emergency}\n\n"
                        "Type 'thanks' to end the consultation.",
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

def send_symptoms_to_api(symptoms: List[str]) -> Optional[Dict]:
    """Envoie les symptômes à l'API Node.js et retourne la réponse."""
    try:
        response = requests.post(
            NODE_API_URL,
            json={"symptoms": symptoms},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error sending symptoms to API: {str(e)}")
        return None 
    













import json
import logging

logger = logging.getLogger(__name__)

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
            patient.conversation_state = 'initial'
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
            elif message in ['2', 'quitter', 'quit']:
                patient.conversation_state = 'initial'
                patient.save()
                logger.info(f"New state: {patient.conversation_state}")
                return get_message('goodbye', language)
            else:
                return get_message('invalid_choice', language)
        
        elif state == 'attente_symptomes':
            # Récupérer les symptômes de l'utilisateur
            symptoms = [s.strip() for s in message.split(',')]  # Séparer les symptômes par des virgules
            logger.info(f"Symptoms received: {symptoms}")
            
            # Envoyer les symptômes à l'API Node.js
            api_response = send_symptoms_to_api(symptoms)
            if not api_response:
                return get_message('error', language)
            
            # Extraire les informations de la réponse de l'API
            disease = api_response.get("maladie", "Inconnu")
            description = api_response.get("description", "Aucune description disponible")
            severity = api_response.get("severity", 1)
            medecins = api_response.get("medecins", [])
            
            # Construire l'objet hospital à partir des informations du premier médecin
            hospital = {}
            if medecins and isinstance(medecins, list):
                medecin = medecins[0] if medecins else {}
                if isinstance(medecin, dict):
                    hospital = {
                        "name": medecin.get("adresse", "Inconnu"),  # Utiliser l'adresse du médecin comme nom de l'hôpital
                        "address": medecin.get("adresse", "Inconnu"),
                        "phone": medecin.get("telephone", "Inconnu"),  # Utiliser le numéro de téléphone du médecin
                        "emergency": True  # Service d'urgence par défaut
                    }
            
            # Stocker les informations dans le patient (pour une utilisation ultérieure)
            patient.current_disease = disease
            patient.current_medecins = json.dumps(medecins)  # Convertir en JSON pour stockage
            patient.current_hospital = json.dumps(hospital)  # Convertir en JSON pour stockage
            patient.conversation_state = 'proposition_actions'
            patient.save()
            logger.info(f"New state: {patient.conversation_state}")
            
            # Retourner les informations à l'utilisateur
            return get_message('disease_found', language,
                             disease=disease,
                             description=description,
                             severity=MESSAGES[language]['severity_levels'].get(severity, "Inconnu"))
        
        elif state == 'proposition_actions':
            if message == '1':  # Recherche médecin
                # Désérialiser les médecins depuis JSON
                try:
                    medecins = json.loads(patient.current_medecins) if patient.current_medecins else []
                except json.JSONDecodeError:
                    medecins = []
                
                if medecins and isinstance(medecins, list):  # Vérifier que c'est une liste
                    medecin = medecins[0] if medecins else {}
                    if isinstance(medecin, dict):  # Vérifier que c'est un dictionnaire
                        return get_message('doctor_found', language,
                                         name=f"{medecin.get('prenom', '')} {medecin.get('nom', '')}",
                                         hospital=medecin.get("adresse", "Inconnu"),
                                         phone=medecin.get("telephone", "Inconnu"),
                                         languages=medecin.get("langues", "Inconnu"))
                return get_message('no_doctor', language)
            
            elif message == '2':  # Recherche hôpital
                # Désérialiser l'hôpital depuis JSON
                try:
                    hospital = json.loads(patient.current_hospital) if patient.current_hospital else {}
                except json.JSONDecodeError:
                    hospital = {}
                
                if hospital and isinstance(hospital, dict):  # Vérifier que c'est un dictionnaire
                    return get_message('hospital_found', language,
                                     name=hospital.get("name", "Inconnu"),
                                     address=hospital.get("address", "Inconnu"),
                                     phone=hospital.get("phone", "Inconnu"),
                                     emergency='✅' if hospital.get("emergency", False) else '❌')
                else:
                    return get_message('no_hospital', language)
            
            elif message == '3':  # Fin de consultation
                patient.conversation_state = 'initial'
                patient.save()
                logger.info(f"New state: {patient.conversation_state}")
                return get_message('consultation_saved', language)
            
            else:
                return get_message('invalid_choice', language)
        
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