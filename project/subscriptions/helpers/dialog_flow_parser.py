DIALOGFLOW_ADDRESS = 'address'
DIALOGFLOW_TIME_PERIOD = 'time-period'
DIALOGFLOW_TIME_PERIOD_START = 'startTime'
DIALOGFLOW_TIME_PERIOD_END = 'endTime'


def get_value_from_dialogflow_context(data, key):
    output_context = data['queryResult']['outputContexts']
    for item in output_context:
        parameter = item['parameters']
        data = parameter.get(key)
        if data:
            break
    return data
