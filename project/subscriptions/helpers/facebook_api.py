import json
import requests


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
