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


class FacebookMessage:
    url = "https://graph.facebook.com/v7.0/me/messages"
    headers = {
        'Content-Type': 'application/json',
    }

    message = None

    def __init__(self, access_token):
        self.params = (
            ('access_token',
             access_token),
        )

    def build_text_message(self, user_psid, message):
        self.message = {
            "recipient": {"id": user_psid},
            "message": {"text": message}
        }

        self.message = json.dumps(self.message)

    def send_message(self, user_psid, message):
        self.build_text_message(user_psid, message)
        res = self.deliver_facebook_message()
        return res

    def deliver_facebook_message(self):
        response = requests.post(self.url, headers=self.headers, params=self.params,
                                 data=self.message)
        return response.content
