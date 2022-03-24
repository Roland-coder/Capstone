def processRequest(req):


    result = req.get("queryResult")
    
    #Fetching the data points
    parameters = result.get("parameters")
    chat_text=parameters.get("text")
    
    
    
    
    
    def cleaning_text(text):
    stop_words = stopwords.words("english")

    # removing urls from tweets
    text = re.sub(r'http\S+', " ", text)    
    # remove mentions
    text = re.sub(r'@\w+',' ',text)         
    # removing hastags
    text = re.sub(r'#\w+', ' ', text)       
    # removing html tags
    text = re.sub('r<.*?>',' ', text)       
    
    # removing stopwords stopwords 
    text = text.split()
    text = " ".join([word for word in text if not word in stop_words])

    for punctuation in string.punctuation:
        text = text.replace(punctuation, "")
    
    return text
    
    df['Text'] = df['text'].apply(lambda x: cleaning_text(x)) 
    new_text = cleaning_text(chat_text)
    
    
    
    
    
    
    
    
    
    
    
   

if __name__ == '__main__':
    app.run()
