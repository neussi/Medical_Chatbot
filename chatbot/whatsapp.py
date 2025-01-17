from twilio.rest import Client
from django.conf import settings

class WhatsAppHandler:
    def __init__(self):
        self.account_sid = 'AC866413181fef5ca1825f87d9d79e1b79'
        self.auth_token = '61f44df78ae234d32e95fcd96c942e24'  # Assurez-vous que c'est le bon token
        self.client = Client(self.account_sid, self.auth_token)
        self.whatsapp_number = 'whatsapp:+14155238886'

    def format_whatsapp_number(self, number):
        """
        Format phone number for WhatsApp
        """
        number = number.strip().replace(" ", "").replace("-", "")
        if "whatsapp:" in number:
            number = number.replace("whatsapp:", "")
        if not number.startswith("+"):
            number = "+" + number
        return f"whatsapp:{number}"

    def send_message(self, to_number, message):
        """
        Send a WhatsApp message to a specific number
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

    def send_template_message(self, to_number, template_sid, variables=None):
        """
        Send a template message
        """
        try:
            formatted_number = self.format_whatsapp_number(to_number)
            message_data = {
                'from_': self.whatsapp_number,
                'content_sid': template_sid,
                'to': formatted_number
            }
            
            if variables:
                message_data['content_variables'] = variables

            message = self.client.messages.create(**message_data)
            return {"success": True, "message_sid": message.sid}
        except Exception as e:
            print(f"Erreur lors de l'envoi du template: {str(e)}")
            return {"success": False, "error": str(e)}