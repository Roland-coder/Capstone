import numpy as np
from flask import Flask, request, make_response
import json
import pickle

app = Flask(__name__)
model = pickle.load(open('intent_model.sav', 'rb'))

@app.route('/')
def hello():
    return 'Hello World. This is Neba, trying out a Medical Prediction Application.'

# geting and sending response to dialogflow
@app.route('/webhook', methods=['POST'])
def webhook():

    req = request.get_json(silent=True, force=True)
    res = processRequest(req)
    res = json.dumps(res)

    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r  #Final Response sent to DialogFlow

def processRequest(req):    # This method processes the incoming request 

    result = req.get("queryResult")
    parameters = result.get("parameters")
    symptom=parameters.get("symptom")
    
    intent = result.get("intent").get('displayName')
    
    if (intent=='DataYes'):
        prediction = model.predict([[symptom]])
        output = round(prediction[0], 2)       
       
        fulfillmentText= "The right medical intent of what you are currently experiencing is:  {} !".format(output)

        return {
            "fulfillmentText": fulfillmentText
        }

if __name__ == '__main__':
    app.run()
