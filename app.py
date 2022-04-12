import numpy as np
from flask import Flask, request, make_response
import json
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer, TfidfVectorizer
import re
import string

import pickle
from spacy.lang.en.stop_words import STOP_WORDS
from nltk.stem import WordNetLemmatizer 
import nltk


from flask_cors import cross_origin



app = Flask(__name__)
# Data preparation, cleaning the text in the dataset

def clean_txt(docs):

    # 
    lemmatizer = WordNetLemmatizer() 

    speech_words = nltk.word_tokenize(docs)

    lower_text = [w.lower() for w in speech_words]

    re_punc = re.compile('[%s]' % re.escape(string.punctuation))
    
    stripped = [re_punc.sub('', w) for w in lower_text]
    
    words = [word for word in stripped if word.isalpha()]
    
    words = [w for w in words if not w in  list(STOP_WORDS)]
    
    words = [word for word in words if len(word) > 2]
    
    lem_words = [lemmatizer.lemmatize(word) for word in words]
    combined_text = ' '.join(lem_words)
    return combined_text

model = pickle.load(open('bagging_model', 'rb'))

@app.route('/')
def hello():
    return """
    
    <h1> Hello World. This is Neba, trying out a Medical Prediction Application.</h1>
    <iframe
    allow="microphone;"
    width="350"
    height="430"
    src="https://console.dialogflow.com/api-client/demo/embedded/ebcc1be7-015e-469f-be2d-2836d3f4d572">
    </iframe>
    
    """

# geting and sending response to dialogflow
@app.route('/webhook', methods=['POST'])
@cross_origin()

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
    symptom = clean_txt(symptom)
    
    if (intent=='predict-intent'):
#         for_pred = [clean_txt(symptom)]
        
        output = model.predict([symptom])[0]
#         output = round(prediction[0], 2)       
       
        fulfillmentText= "The right medical intent of what you are currently experiencing is:  {} ! \n Do you wish you describe any other symptom ???".format(output)

        return {
            "fulfillmentText": fulfillmentText
        }

if __name__ == '__main__':
    app.run()
