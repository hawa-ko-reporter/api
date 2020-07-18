def prepare_aqi_message(data):
    messages = ["The nearest station is {}".format(data['station']['name']),
                "It is {:.1f} km away".format(data['distance']), "The AQI is {} at {}".format(
            data['message']['level'], data['aqi']), "I would say {} ".format(data['message']['health']),
                "Do you want more tips?"]

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


def get_aqi_response_message(aqi, data):
    messages = prepare_aqi_message(aqi)
    reply = multiline_message(message_list=messages)
    reply = add_output_context(reply, data=data, aqi=aqi)
    return reply


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
