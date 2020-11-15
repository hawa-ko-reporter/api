DIALOGFLOW_ADDRESS = 'address'
DIALOGFLOW_TIME_PERIOD = 'time-period'
DIALOGFLOW_TIME_PERIOD_START = 'startTime'
DIALOGFLOW_TIME_PERIOD_END = 'endTime'

def get_value_from_dialogflow_alt_context(data,key):
  try:
    output_context_alt = data['alternativeQueryResults'][0]['outputContexts']
    for item in output_context_alt:
        parameter = item['parameters']
        data = parameter.get(key)
        if data:
          break
    return data
  except:
    return ""

def get_value_from_dialogflow_context(data,key):
  output_context = data['queryResult']['outputContexts']
  for item in output_context:
    parameter = item['parameters']
    data = parameter.get(key)
    if data:
      break
  return data