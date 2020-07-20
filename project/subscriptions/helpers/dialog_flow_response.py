def prepare_aqi_message(data):
    messages = ["The nearest station is {}".format(data['station']['name']),
                "It is {:.1f} km away".format(data['distance']), "The AQI is {} at {}".format(
            data['message']['level'], data['aqi']), "I would say {} ".format(data['message']['health']),
                "Do you want more tips?"]

    return messages


def get_aqi_image(aqi):
    size = "500x300"
    aqi = int(aqi)
    if aqi <= 50:
        return "https://dummyimage.com/{}/00e400/000000.png&text={}".format(size, aqi)
    elif aqi <= 100:
        return "https://dummyimage.com/{}/ffff00/000000.png&text={}".format(size, aqi)
    elif aqi <= 150:
        return "https://dummyimage.com/{}/ff7e00/ffffff.png&text={}".format(size, aqi)
    elif aqi <= 200:
        return "https://dummyimage.com/{}/ff0000/ffffff.png&text={}".format(size, aqi)
    elif aqi <= 300:
        return "https://dummyimage.com/{}/8f3f97/ffffff.png&text={}".format(size, aqi)
    else:
        return "https://dummyimage.com/{}/7e0023/ffffff.png&text={}".format(size, aqi)


def prepare_aqi_message_v2(data):
    return {
        'title': "AQI is at {}".format(data['aqi']),
        'description': "It is considered {} ".format(data['message']['level']),
        'image_url': get_aqi_image(data['aqi']),
        'map_url': "https://www.google.com/maps/search/?api=1&query={},{}".format(data['lat'], data['lon']),
        'message': [
            "It is {:.1f} km away".format(data['distance']),
            "I would say {} ".format(data['message']['health']),
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
    messages = prepare_aqi_message_v2(aqi)

    reply = fb_card_message(title=messages.get('title'), message=messages.get("description"),
                            maps_url=messages.get("map_url"), image_url=messages.get("image_url"),
                            messages=messages.get("message"))

    reply = add_output_context(reply, data=data, aqi=aqi)
    return reply


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
