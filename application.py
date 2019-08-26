    # /index.py

from flask import Flask, request, jsonify, render_template
import os
import dialogflow
import requests
import json
import pusher
import requests


app = Flask(__name__)


## The default route shows a web page . use for testing only
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])

def webhook():
    data = request.get_json(silent=True)
    action = data['queryResult']['action']   
    if action == 'get_uvreading': 
        return get_uvreading(data)
    elif action == "test_connection" :
        return test_connection(data)
    else:
        return handle_unknown_action(data)

def test_connection(data):
   response = {}
   replytext = "Hi there. You have made a successful connection to the webhook. Yeah !"
   response["fulfillmentText"] = replytext
   return jsonify(response)  
    
def handle_unknown_action(data):
   response = {}
   replytext = "Oh dear! Your request for action " + data['queryResult']['action']  + "is challenging! Can't do it do."
   response["fulfillmentText"] = replytext
   return jsonify(response)            
        

def get_uvreading(data):   
# This function sends a get request to data.gov.sg to gets
# a json return that provides latest UV readings

    url = "https://api.data.gov.sg/v1/environment/uv-index"  
    r = requests.get(url) # makes a request to data.gov.sg
   
    if r.status_code == 200:
        data = r.json()  # get the serialised json response returned as a dictionary
        last_readingtimestamp = data["items"][0]["timestamp"]
        last_uvlevel = data["items"][0]["index"][0]["value"]
        agent_advice = explain_uvindex(last_uvlevel)
        replytext = "The UV indes is at level  " + str(last_uvlevel) + ". " + agent_advice
    else:
        replytext = "I can't get the data. Can you look out the window instead?"

    response = {}
    response["fulfillmentText"] = replytext
    return jsonify(response)    



def explain_uvindex(value):
# This function interprets the uv index. 
# Source: https://en.wikipedia.org/wiki/Ultraviolet_index
    if value < 2.9:
        text = "There is low danger from the sun ray for the average person. Wear sunglasses if it is bright."
    elif value < 5.9 :
        text = "There is a moderate risk of harm from unprotected sun exposure.  Stay in shade near the mid-day."   
    elif value < 7.9:
        text = "There is a high risk of harm from unprotected sun exposure. You need protection against skill and eye damages."
    else:
        text = "Wow ! The UV index is very high. I suggest that you stay in the shade."
    return text


# run Flask app
if __name__ == "__main__":
        app.run()