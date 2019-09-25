    # /index.py

from flask import Flask, request, jsonify, render_template
import os
import dialogflow
import requests
import json
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials



app = Flask(__name__)


## The default route shows a web page . use for testing only
@app.route('/')
def index():
    return ('Flask Application Is Deployed.')

@app.route('/webhook', methods=['POST'])

def webhook():
# action refers to the action value defined in Dialogflow for the selected intent
# Here, we are checking for the intent (through action) which call the services
    data = request.get_json(silent=True)
    action = data['queryResult']['action']   
    elif action == "test_connection" :
        return test_connection(data)
    elif action == "request_callback" :
        return request_callback(data)
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
        

def request_callback(data):
## this function is called if the action == request_callback
## in Dialogflow, you should have the two parameters "phone-number" and "person"
   phone = data['queryResult']['parameters']['phone-number']
   name =  data['queryResult']['parameters']['person']['name']
   querytext = data['queryResult']['queryText']
## Need to insert codes to write to excel file                
   scope = ['https://spreadsheets.google.com/feeds',  'https://www.googleapis.com/auth/drive']
   creds = ServiceAccountCredentials.from_json_keyfile_name('REPLACE WITH SERVICE KEY FILE FROM GOOGLE.json', scope)
   client = gspread.authorize(creds)
# Find a workbook by name and open the first sheet
# Make sure you use the right name here.
   sheet = client.open("REPLACE WITH YOUR GOOGLE SHEET NAME").sheet1

   values = [name, phone, querytext]
   # the next line appends a row containing 3 rows to the spreadsheet
   sheet.append_row(values, value_input_option='RAW')

# Prepare a response
   response = {}
   replytext = "Hi "  + name + ", we will call you back at " + phone + ". Talk to you soon."
   response["fulfillmentText"] = replytext
   return jsonify(response)  

# run Flask app
if __name__ == "__main__":
        app.run()