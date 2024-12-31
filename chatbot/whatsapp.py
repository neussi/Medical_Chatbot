# chatbot/whatsapp.py
from twilio.rest import Client
from django.conf import settings
import json

class WhatsAppHandler:
    def __init__(self):
        self.account_sid = "AC866413181fef5ca1825f87d9d79e1b79"
        self.auth_token = "[61f44df78ae234d32e95fcd96c942e24]"  
        self.client = Client(self.account_sid, self.auth_token)
        self.whatsapp_number = "whatsapp:+14155238886" 

    def format_whatsapp_number(self, number):
        """
        Formate correctement le numéro pour WhatsApp
        """
        number = number.strip().replace(" ", "").replace("-", "")
        
        if "whatsapp:" in number:
            number = number.replace("whatsapp:", "")
            
        if not number.startswith("+"):
            number = "+" + number
            
        return f"whatsapp:{number}"

    def send_message(self, to_number, message):
        """
        Envoie un message WhatsApp à un numéro spécifique
        """
        try:
            formatted_number = self.format_whatsapp_number(to_number)
            message = self.client.messages.create(
                from_=self.whatsapp_number,
                body=message,
                to=formatted_number
            )
            return {"success": True, "message_sid": message.sid}
        except Exception as e:
            print(f"Erreur lors de l'envoi du message: {str(e)}")
            return {"success": False, "error": str(e)}