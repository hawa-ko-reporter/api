from django.utils.timezone import localdate
from subscriptions.helpers.air_quality_fetcher import get_aqi_code

from subscriptions.models import Recommendation
import random

from subscriptions.models import AQIRequestLog


def prepare_aqi_message(data):
    messages = ["The nearest station is {}".format(data['station']['name']),
                "{:.1f} km away".format(data['distance']), "The AQI is {} at {}".format(
            data['message']['level'], data['aqi']), "I would say {} ".format(data['message']['health']),
                "Do you want more tips?"]

    return messages


def get_aqi_message(aqi):
    size = "500x300"
    image = None
    message = None

    try:
        aqi = int(aqi)
    except ValueError:
        image = "https://dummyimage.com/{}/ffffff/000000.png&text={}".format(size, "-")
        return image,message


    if aqi <= 50:
        image = "https://dummyimage.com/{}/00e400/000000.png&text={}".format(size, aqi)
    elif aqi <= 100:
        image = "https://dummyimage.com/{}/ffff00/000000.png&text={}".format(size, aqi)
    elif aqi <= 150:
        image = "https://dummyimage.com/{}/ff7e00/ffffff.png&text={}".format(size, aqi)
    elif aqi <= 200:
        image = "https://dummyimage.com/{}/ff0000/ffffff.png&text={}".format(size, aqi)
    elif aqi <= 300:
        image = "https://dummyimage.com/{}/8f3f97/ffffff.png&text={}".format(size, aqi)
    else:
        image = "https://dummyimage.com/{}/7e0023/ffffff.png&text={}".format(size, aqi)

    return image, message


def prepare_aqi_message_v2(data):
    image, message = get_aqi_message(data['aqi'])
    return {
        'title': "AQI is at {} in {} station".format(data['aqi'], data['station']['name']),
        'description': "It is considered {} ".format(data['health']),
        'image_url': image,
        'map_url': "https://www.google.com/maps/search/?api=1&query={},{}".format(data['lat'], data['lon']),
        'message': [
            "It is {:.1f} km away from {}".format(data['distance'], data['street_display_name']),
            "I would say {} ".format(data['message']),
            "Do you want more tips?"
        ]
    }


class DialogFlowMessage:
    reply = {}

    def buildMessage(self, name, data):
        if name == 'station-report':
            messages = self.prepare_aqi_message(data)
            self.reply = multiline_message(message_list=messages, reply={})

        return self.reply

    @staticmethod
    def multiline_message(message_list):
        reply = {}
        processed_messages = []
        for message in message_list:
            processed_messages.append({
                "text": {
                    "text": [
                        str(message)
                    ]
                }
            })
        reply['fulfillmentMessages'] = processed_messages
        return reply

    @staticmethod
    def prepare_aqi_message(data):
        messages = ["The AQI at {} is {}".format(data['station']['name'], data['aqi']),
                    "It is {}".format(
                        data['message']['level'], ), ]
        return messages


def add_output_context(dialogflow_reply, data, aqi):
    dialogflow_reply["outputContexts"] = [
        {
            "name": "{}/contexts/data-upsell-yes".format(data['session']),
            "lifespanCount": 1,
            "parameters": {
                "aqi": float(aqi['aqi']),
            }
        }
    ]
    return dialogflow_reply


def get_list_subs_response_message(subscriptions):
    messages = prepare_subscriptions_message(subscriptions)
    reply = multiline_message(message_list=messages, reply={})
    return reply


def prepare_subscriptions_message(subscriptions):
    messages = ["You are subscribed to {} stations".format(len(subscriptions))]
    for row in subscriptions:
        messages.append(row.subscription.name)
    messages.append("Do you want to un-subscribe?")
    return messages


def get_aqi_response_message(aqi, data):
    print(aqi['aqi'])
    print(aqi)
    messages = prepare_aqi_message_v2(aqi)

    reply = fb_card_message(title=messages.get('title'), message=messages.get("description"),
                            maps_url=messages.get("map_url"), image_url=messages.get("image_url"),
                            messages=messages.get("message"))

    reply = add_output_context(reply, data=data, aqi=aqi)
    return reply


def generate_random_queries(sample_size):
    queries = ['best mask pollution', 'is cloth mask good?', 'KN95 vs N95 mask', 'is value mask good?']
    return random.choice(queries)


def multiple_stations_slider_report_stations(stations):
    fulfillment_messages = {}
    elements = []
    recommendation = None

    aqi_table_url = "https://i.ibb.co/mNF1nB6/aqi-table.png"
    aqi_table_url = "https://i.ibb.co/bJ0VmZS/aqi-table-v2.png"
    aqi_table_url = "https://i.ibb.co/M7B518f/aqi-table-v3.png"

    elements.append(
        fb_template_card(image_url=aqi_table_url, title="Understanding AQI", maps_url=aqi_table_url,
                         message="The table "
                                 "below "
                                 "defines "
                                 "the Air "
                                 "Quality "
                                 "Index "
                                 "scale as "
                                 "defined "
                                 "by the "
                                 "US-EPA "
                                 "2016 "
                                 "standard:"))

    for station in stations:

        image_url, message = get_aqi_message(station['aqi'])
        maps_url = "https://www.google.com/maps/search/?api=1&query={},{}".format(station['lat'], station['lon'])

        full_url = 'https://3955fe4a9643.ngrok.io/aqi/?id={}'.format(station['uid'])
        full_url = 'https://hawa.naxa.com.np/aqi/?id={}'.format(station['uid'])


        station_name = station.get('station').get('name')
        title = "{} (Approx. {:.1f} KM away)".format(station_name, station['distance'])
        aqi_code, health = get_aqi_code(aqi=station['aqi'])
        if aqi_code != -1:
            message = "This is considered {} ".format(health)
        else:
            message = health
        elements.append(
            fb_template_card(title=title,
                             image_url=image_url,
                             maps_url=full_url,
                             message=message
                             ))
        if recommendation is None:
            recommendation = Recommendation.objects.filter(recommendation_category=aqi_code).order_by('?').first()

            if recommendation is not None:
                recommendation = "I would say {}".format(recommendation.recommendation_text)

    fb_custom_payload = {

        'payload': {
            'facebook': {
                'attachment': {'type': 'template', 'payload': {'template_type': 'generic',
                                                               'elements': elements}}
            }
        },
        'platform': "FACEBOOK"

    }

    quick_replies = ['Send Daily']
    queries = generate_random_queries(1)
    print(queries)
    quick_replies.append(queries)
    fulfillment_messages["fulfillmentMessages"] = [
        fb_text("I found these stations nearby "),
        fb_text("Swipe right ➡➡️️"),
        fb_custom_payload,
        fb_text(recommendation),
        fb_text("You know! I can send these to you daily automatically"),
        fb_quick_replies("Choose the option 'send daily' to subscribe",
                         quick_replies)
                         ]

    return fulfillment_messages


def geocode_failure_reply():
    fulfillment_messages = {"fulfillmentMessages": []}
    fulfillment_messages['fulfillmentMessages'].append(fb_text("Oh! I don't know that address!"))
    fulfillment_messages['fulfillmentMessages'].append(fb_text("Say a different address"))
    fulfillment_messages['fulfillmentMessages'].append(
        fb_quick_replies("or choose a option", ["Cancel", "AQI at Kathmandu", "AQI at Pokhara","AQI at Dharan"]))

    return fulfillment_messages

def confirm_geo_code_location(display_name):
    fulfillment_messages = {"fulfillmentMessages": []}

    fulfillment_messages['fulfillmentMessages'].append(fb_text("Oh! *{}*?".format(display_name)))
    fulfillment_messages['fulfillmentMessages'].append(fb_text("Is that the right address?"))
    fulfillment_messages['fulfillmentMessages'].append(
        fb_quick_replies("Choose a option or reply:", ["Cancel", "Yes", "No"]))
    return fulfillment_messages


def welcome_message(name, user):
    message_without_name = ["Great to see you again {}".format(name),
                            "Hello {}! Hope you are staying safe in this pandemic.".format(name)]

    messages_with_name = ["Hey, I am hawa-ko-reporter, Nice to meet you."
                          "I am able to report air quality information of places in Nepal."
                          "I do this by searching real - time air pollution open data on the web.",

                          "Namaste! {} I am Hawa ko Reporter the coolest chat bot here to "
                          "let you know about things associated with air quality. "
                          "I am in your service to fulfill your queries. "
                          "Please choose what would you like to know about".format(name),

                          "Hey {}! nice to connect with you. I am Hawa ko Reporter"
                          " a chat-bot designed to clear people’s confusion primarily about "
                          "the air quality and factors associated with it. "
                          "Please select what you are interested in knowing about".format(name),
                          "Hello {}! Hope you are staying safe in this pandemic. "
                          "Btw I am Hawa ko Reporter a chat-bot. I have been assigned to "
                          "help you to know about the air quality. What information would you like to et from me?".format(
                              name)
                          ]

    messages = messages_with_name if name is None else message_without_name

    fulfillment_messages = {"fulfillmentMessages": []}
    fulfillment_messages['fulfillmentMessages'].append(fb_text(random.choice(messages)), )
    if name is None:
        fulfillment_messages['fulfillmentMessages'].append(fb_text("Try it now! Choose a option below"))
        fulfillment_messages['fulfillmentMessages'].append(
            fb_quick_replies("👋", ["Air quality near me",  "What is AQI?",generate_random_queries(1)]))
    else:
        fulfillment_messages['fulfillmentMessages'].append(fb_text("What would you like to ask today?"))

        logs = AQIRequestLog.objects.filter(
            user=user,
            created__startswith=str(localdate())
        ).order_by('-created')[0:2]
        print(logs)

        previous_locations = ["Air quality near me", "What is AQI?",generate_random_queries(1)]
        for log in logs:
            previous_locations.append("aqi at %s" % log.location_name)

        fulfillment_messages['fulfillmentMessages'].append(fb_text("What would you like to ask today?"))
        fulfillment_messages['fulfillmentMessages'].append(
            fb_quick_replies("👋", previous_locations))

    return fulfillment_messages


def multiple_stations_report(stations):
    fulfillment_messages = {"fulfillmentMessages": []}

    for station in stations:
        image_url, message = get_aqi_message(station['aqi'])
        maps_url = "https://www.google.com/maps/search/?api=1&query={},{}".format(station['lat'], station['lon'])
        print(station)

        fulfillment_messages['fulfillmentMessages'].append(
            fb_card(title=station.get('station').get('name'),
                    image_url=image_url,
                    maps_url=maps_url,
                    message=message
                    ))

    return fulfillment_messages


def fb_quick_replies(title, replies):
    quick_replies = {
        "quickReplies": {
            "title": title,
            'quickReplies': replies
        },
        'platform': "FACEBOOK"
    }

    return quick_replies


def fb_text(text):
    return {
        "text": {
            "text": [
                text
            ]
        },
        "platform": "FACEBOOK"
    }


def fb_template_button(title, url):
    return {
        "type": "web_url",
        "url": url,
        "title": title
    }


def fb_template_card(title, message, image_url, maps_url):
    return {
        "title": title,
        "subtitle": message,
        "image_url": image_url,
        "default_action": {
            "type": "web_url",
            "url": maps_url,
            "webview_height_ratio": "COMPACT"
        },
        "buttons": [fb_template_button("View Details", maps_url)]
    }


def fb_card(title, message, image_url, maps_url):
    return {
        "card": {
            "title": title,
            "subtitle": message,
            "imageUri": image_url,
            "buttons": [
                {
                    "text": "View Station location",
                    "postback": maps_url
                },
            ]
        },
        "platform": "FACEBOOK"
    }


def fb_card_message(title, message, image_url, maps_url, messages):
    return {
        "fulfillmentMessages": [
            {
                "card": {
                    "title": title,
                    "subtitle": message,
                    "imageUri": image_url,
                    "buttons": [
                        {
                            "text": "View Station location",
                            "postback": maps_url
                        },
                    ]
                },
                "platform": "FACEBOOK"
            },
            {
                "text": {
                    "text": [
                        messages[0]
                    ]
                },
                "platform": "FACEBOOK"
            },
            {
                "text": {
                    "text": [
                        messages[1]
                    ]
                },
                "platform": "FACEBOOK"
            },
            {
                "text": {
                    "text": [

                    ]
                },
                "platform": "FACEBOOK"
            },
            {
                "quickReplies": {
                    "title": messages[2],
                    "quickReplies": [
                        "Get Daily"
                    ]
                },
                "platform": "FACEBOOK"
            },
        ],
    }


def single_line_message(message):
    return {'fulfillmentText': message}


def multiline_message(message_list, reply):
    processed_messages = []
    for message in message_list:
        processed_messages.append({
            "text": {
                "text": [
                    str(message)
                ]
            }
        })

    reply['fulfillmentMessages'] = processed_messages
    return reply
