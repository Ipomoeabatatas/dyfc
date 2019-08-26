    # /index.py

from flask import Flask, request, jsonify, render_template
import os
import dialogflow
import requests
import json
import pusher
import requests

# Andy's:
import reclib

app = Flask(__name__)


## Th default route shows a web page . use for testing only
@app.route('/')
def index():
    return render_template('index.html')

## www.xxx/webhook is what you put into the dialogflow
## Within it, it will match to the action name and invole the neccessary function

@app.route('/webhook', methods=['POST'])

def webhook():
    data = request.get_json(silent=True)
    action = data['queryResult']['action']
    
    if (action == 'recommendPizza'): 
        return recommend_pizza(data)
        
    if (action == 'recommendMovie'): 
        return recommend_movie(data)    
        
## FOOMENG: Work within the function   
def recommend_movie(data):
   # data = request.get_json(silent=True)
    movie_A = data['queryResult']['parameters']['boringMovie']
    movie_B = data['queryResult']['parameters']['favMovie']
    movie_C = data['queryResult']['parameters']['interestingMovie']
#    favGenre = data['queryResult']['parameters']['favGenre']
#    dislikeGenre = data['queryResult']['parameters']['dislikeGenre']
    custName = data['queryResult']['parameters']['custName'] 
#    custId  = data['queryResult']['parameters']['custId'] 
    #FOOMENG: FOOMENG: Change only between the $$$$$$$$$$$$$$$$$$$$$$$$$
    
    #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    #FOOMENG: Put your names of the movies into the Array moviesrecommend. Keep to 3.
    #FOOMEWG: Put the url for the images into url1 to url3
    
    # movieswatched = ["Y1", "Y2 ", "Y3", "Y4", "Y5"]
    movieRecommendUrl = "http://fa77f83c.ngrok.io"
    r = requests.post(movieRecommendUrl, json={"watched": [movie_A, movie_B, movie_C] }) 
    


## FM to call your web web services using the parameters movie_A, movie_B , movie_C
## FM to process the return JSON and dumpeds in into array moviesrecommend  w1, w2, w3



    #moviesrecommend =["W1", "W2", "W3"]
    moviesrecommend = r.json()["movies"]
    
    
    #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    response = ""
    reply = {
        "fulfillmentText": response,
        "fulfillmentMessages": [   
         {
          "text": {
          "text": [
            "Thanks %s" % custName, 
            "You've told me that you enjoyed the following movies:",
            "1. %s" % movie_A, 
            "2. %s" % movie_B, 
            "3. %s" % movie_C, 
            " ", 
            "Many people who enjoy the above movies also enjoy the titles listed below" ,
            "1. %s" % moviesrecommend[0],
            "2. %s" % moviesrecommend[1],
            "3. %s" % moviesrecommend[2],
           " "            
          ]
          },
            "platform": "TELEGRAM" }, 



                     {
          "text": {
          "text": [
             custName  +  ", would you like to have some pizza when you watch the movie?"            
          ]
          },
            "platform": "TELEGRAM" } 
        ] 
        }

    return jsonify(reply)

# Andy: Work within this function only
def recommend_pizza(data):
#    data = request.get_json(silent=True)

# ANDY: The next 3 variables contains the ranking for 2 types of pizza and custmer ID
    rank1 = data['queryResult']['parameters']['superSupremeRank']
    rank2 = data['queryResult']['parameters']['hawalianRank']
    custName = data['queryResult']['parameters']['custName']
    
#    response1 = "Your input was %s %s and %s" %(rank1, rank2, custId)
    response1 = ""
    response2 = "Ok %s. People who feel the same way about Super Supreme and Hawalli pizzas as you have also rated the pizzas below very positively. You may want to consider them too." % custName
    
    # ANDY: $$$$$$$$$$$$$$$$$$$$
    # ANDY: Put your list of 3 recommended pizzas into the array below.
    reclib.addUser(custName, float(rank2), float(rank1))
    jsonResp = reclib.getReqdFormat(custName)
    
    pizzarecommend =  json.loads(jsonResp)["names"]
    print (pizzarecommend)
    
    listLen = len(pizzarecommend)
    if listLen < 3:
        for i in range(3 - listLen):
            pizzarecommend.append("")
    
    response=""
    reply = {
        "fulfillmentText": response,
        "fulfillmentMessages": [   
         {
          "text": {
          "text": [
            response1,
            response2, 
            "1. %s" % pizzarecommend[0],
            "2. %s" % pizzarecommend[1],
            "3. %s" % pizzarecommend[2],
            "",
            "Use the promotion code REBECCA if you decide to order from www.pizzashop.sg ."
             
          ]
          },
            "platform": "TELEGRAM" }
        ] 
        }
    return jsonify(reply)

    

# run Flask app



if __name__ == "__main__":
        app.run()