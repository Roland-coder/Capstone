import numpy as np
from flask import Flask, request, make_response,session,url_for
from flask_session import Session
import mysql.connector
import json
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer, TfidfVectorizer
from flask import render_template, redirect
import os
import re
import string

import pickle
from spacy.lang.en.stop_words import STOP_WORDS
from nltk.stem import WordNetLemmatizer 
import nltk


from flask_cors import cross_origin


connection = mysql.connector.connect(host='localhost',port='3307',database='medicalPredictApp',user='root',password='mysql')

cursor=connection.cursor()
app = Flask(__name__)
app.secret_key = "super secret key"
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
def homepage():
    return render_template('index.html')

@app.route('/login', methods =['GET','POST'])

def login():
    msg =''
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        cursor.execute('SELECT * FROM user WHERE email=%s AND password = %s',(email,password))
        record = cursor.fetchone()
        if record:
            session['loggedin']=TRUE
            session['username']=redord[1]
            return redirect(url_for('/home')
        else:
             msg = 'Incorrect Email or password'
    return render_template('index.html'msg=msg)

@app.route('/home')
def hello():
    return """
    <div align= "center">
        
        <iframe
        allow="microphone;"
        width="350"
        height="430"
        src="https://console.dialogflow.com/api-client/demo/embedded/ebcc1be7-015e-469f-be2d-2836d3f4d572">
        </iframe>
    </div>
    
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
       
        fulfillmentText= "The right medical intent of what you are currently experiencing is:  {} ! ".format(output)

        return {
            "fulfillmentText": fulfillmentText
        }

if __name__ == '__main__':
    app.run()
