import numpy as np
from flask import Flask, request, make_response
import json
import pickle
# from spacy.lang.en.stop_words import STOP_WORDS
# from nltk.stem import WordNetLemmatizer 


from flask_cors import cross_origin



app = Flask(__name__)
# Data preparation, cleaning the text in the dataset

# def clean_txt(docs):

#     # 
#     lemmatizer = WordNetLemmatizer() 

#     speech_words = nltk.word_tokenize(docs)

#     lower_text = [w.lower() for w in speech_words]

#     re_punc = re.compile('[%s]' % re.escape(string.punctuation))
    
#     stripped = [re_punc.sub('', w) for w in lower_text]
    
#     words = [word for word in stripped if word.isalpha()]
    
#     words = [w for w in words if not w in  list(STOP_WORDS)]
    
#     words = [word for word in words if len(word) > 2]
    
#     lem_words = [lemmatizer.lemmatize(word) for word in words]
#     combined_text = ' '.join(lem_words)
#     return combined_text

model = pickle.load(open('bagging_model', 'rb'))

@app.route('/')
def hello():
    return 'Hello World. This is Neba, trying out a Medical Prediction Application.'

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
    
    if (intent=='predict-intent'):
#         for_pred = [clean_txt(symptom)]
        
        prediction = model.predict([[symptom]])[0]
        output = round(prediction[0], 2)       
       
        fulfillmentText= "The right medical intent of what you are currently experiencing is:  {} !".format(output)

        return {
            "fulfillmentText": fulfillmentText
        }

if __name__ == '__main__':
    app.run()
