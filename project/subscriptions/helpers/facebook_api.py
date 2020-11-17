import json
import requests
import requests
import json


def get_name(psid, access_token):
    params = (
        ('fields', 'first_name,last_name'),
        ('access_token', access_token),
    )
    payload = {'fields': 'first_name', 'access_token': access_token}
    url = 'https://graph.facebook.com/' + psid + "?fields=first_name,last_name&access_token=" + access_token

    response = requests.get(url)

    return response.content


def handle_fb_name_response(content, default_name):
    try:
        content = json.loads(content)
        first_name = content.get('first_name')
        last_name = content.get('last_name')
        return "{} {}".format(first_name, last_name)

    except KeyError:
        return default_name


class FacebookMessageGenerator:
    def generate_aqi_cards(self, messages):
        type = "generic"
        reply_payload = {}
        elements = []
        for message in messages:
            print(message)
            elements.append({
                "title": message.get('title'),
                "image_url": message.get('image_url'),
                "subtitle": message.get('subtitle'),
            })
        reply_payload['payload'] = {'template_type': type, "elements": elements}
        return reply_payload


class FacebookMessageSender:
    url = "https://graph.facebook.com/v8.0/me/messages"
    headers = {
        'Content-Type': 'application/json',
    }

    message = None

    def __init__(self, access_token):
        self.params = (
            ('access_token',
             access_token),
        )
        self.message_generator = FacebookMessageGenerator()

    def build_text_message(self, user_psid, message):
        self.message = {
            "recipient": {"id": user_psid},
            "message": {"text": message}
        }

        self.message = json.dumps(self.message)

    def send_text_message(self, user_psid, message):
        self.build_text_message(user_psid, message)
        res = self.deliver_facebook_message()
        return res

    def build_card_message(self, user_psid, reply_payload):
        self.message = {
            "recipient": {"id": user_psid},
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": reply_payload['payload']}
            }
        }

        self.message = json.dumps(self.message)
        print(self.message)


    def send_card_message(self, user_psid, messages):
        self.build_card_message(user_psid, messages)

        res = self.deliver_facebook_message()
        return res



    def deliver_facebook_message(self):

        response = requests.post(self.url, headers=self.headers, params=self.params,
                                 data=self.message)
        return response.content, response.status_code
