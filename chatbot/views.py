# chatbot/views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from .whatsapp import WhatsAppHandler
from .models import Patient, Conversation
import json

whatsapp_handler = WhatsAppHandler()

def home(request):
    return HttpResponse("La page d'accueil fonctionne!")

@csrf_exempt
def webhook(request):
    if request.method == 'POST':
        # Récupérer les données du message
        incoming_msg = request.POST.get('Body', '').strip()
        sender_number = request.POST.get('From', '')
        
        try:
            # Créer ou récupérer le patient
            patient, created = Patient.objects.get_or_create(
                phone_number=sender_number
            )
            
            # Enregistrer le message entrant
            Conversation.objects.create(
                patient=patient,
                message=incoming_msg,
                is_from_patient=True
            )
            
            # Traiter le message et obtenir la réponse
            response = process_message(incoming_msg, patient)
            
            # Envoyer la réponse via WhatsApp
            whatsapp_handler.send_message(
                to_number=sender_number,
                message=response
            )
            
            return HttpResponse('OK')
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    # Pour les requêtes GET, afficher une page de test
    return HttpResponse("""
        <html>
            <body>
                <h1>Webhook WhatsApp Test</h1>
                <form method="POST" action="/webhook/">
                    <input type="text" name="Body" placeholder="Message">
                    <input type="text" name="From" placeholder="whatsapp:+123456789">
                    <button type="submit">Envoyer</button>
                </form>
            </body>
        </html>
    """)

def process_message(message, patient):
    """
    Traite le message entrant et retourne une réponse appropriée
    """
    # Message de bienvenue par défaut
    if message.lower() in ['bonjour', 'hello', 'hi', 'salut']:
        return ("Bonjour! Je suis votre assistant médical virtuel. "
                "Comment puis-je vous aider aujourd'hui ?")
    
    # Si le message contient des mots-clés liés aux symptômes
    if any(word in message.lower() for word in ['mal', 'douleur', 'symptôme', 'problème']):
        return ("Je vois que vous ne vous sentez pas bien. "
                "Pouvez-vous me décrire plus en détail vos symptômes ?")
    
    # Réponse par défaut
    return ("Je suis désolé, je n'ai pas bien compris. "
            "Pouvez-vous reformuler votre demande ?")

@csrf_exempt
def send_template_example(request):
    template_sid = "HXb5b62575e6e4ff6129ad7c8efe1f983e"
    variables = {
        "1": "12/1",
        "2": "3pm"
    }
    
    whatsapp_handler.send_template_message(
        to_number="+237650970526",
        template_sid=template_sid,
        variables=variables
    )
    
    return HttpResponse('Template sent')