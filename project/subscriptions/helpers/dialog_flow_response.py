def prepare_aqi_message(data):
    messages = ["The nearest station is {}".format(data['station']['name']),
                "It is {:.1f} km away".format(data['distance']), "The AQI is {} at {}".format(
            data['message']['level'], data['aqi']), "I would say {} ".format(data['message']['health']),
                "Do you want more tips?"]

    return messages


def rich_card_response(title, message, image):
    return {
        "card": {
            "title": "Card Title",
            "subtitle": "Card subtitle",
            "imageUri": "https://github.com/fluidicon.png",
            "buttons": [
                {
                    "text": "Go to Google",
                    "postback": "www.google.com"
                },
                {
                    "text": "Go to Dialogflow",
                    "postback": "www.dialogflow.com"
                },
                {
                    "text": "Go to Slack",
                    "postback": "www.slack.com"
                }
            ]
        },
        "platform": "FACEBOOK"
    }


class DialogFlowMessage:
    reply = {}

    def buildMessage(self, name, data):
        if name == 'station-report':
            messages = self.prepare_aqi_message(data)
            self.reply = multiline_message(message_list=messages)

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
            "lifespanCount": 5,
            "parameters": {
                "aqi": float(aqi['aqi']),
            }
        }
    ]
    return dialogflow_reply


def get_list_subs_response_message(subscriptions):
    messages = prepare_subscriptions_message(subscriptions)
    reply = multiline_message(message_list=messages)
    return reply


def prepare_subscriptions_message(subscriptions):
    messages = ["You are subscribed to {} stations".format(len(subscriptions))]
    for row in subscriptions:
        messages.append(row.subscription.name)
    messages.append("Do you want to un-subscribe?")
    return messages


def get_aqi_response_message(aqi, data):
    messages = prepare_aqi_message(aqi)
    reply = multiline_message(message_list=messages)
    reply = add_output_context(reply, data=data, aqi=aqi)
    return reply


def single_line_message(message):
    return {'fulfillmentText': message}


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
