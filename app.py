import numpy as np
from flask import Flask, request, make_response,session,url_for
import psycopg2
import json
import mysql.connector
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
# connection = mysql.connector.connect(host='ec2-34-207-12-160.compute-1.amazonaws.com',port='5432',
#                                      database='d90tl94u97uha4', user='wlnvcqrrmxbved', 
#                                      password='2893e389d4a71557c25ca55b9a9602e60a75ec514cf497cfcee14291bbbc79bf')



# cursor=connection.cursor()
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

# @app.route('/login', methods =['GET','POST'])

# def login():
#     msg =''
#     if request.method == "POST":
#         email = request.form['email']
#         password = request.form['password']
#         cursor.execute('SELECT * FROM user WHERE email=%s AND password = %s',(email,password))
#         record = cursor.fetchone()
#         if record:
#             session['loggedin']=TRUE
#             session['username']=redord[1]
        
#             return redirect(url_for('/home'))
#         else:
#             msg = 'Incorrect Email or password'       
    
#     return render_template('index.html', msg=msg)

@app.route('/home')
def hello():
    return render_template('home.html',session['username'])

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
