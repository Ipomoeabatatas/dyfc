    # /index.py

from flask import Flask, request, jsonify
import os
import json
import requests
import pandas as pd
import numpy as np
from re import search
import gspread
from oauth2client.service_account import ServiceAccountCredentials

### PLEASE MODIFY THE NEXT TWO LINES TO CUSTOMIZE TO YOUR OWN GOOGLESHEET ###

KEY_FILE = "PythonToSheet-46f0bfa4bace.json"        
GOOGLE_SHEET_WRITE = "OneChatBotCourse"                   
GOOGLE_SHEET_READ_URL  = "https://docs.google.com/spreadsheets/d/1z-RSuTmq8-jb7UmgFDx3JMJiLBkRSZy8wsqNb2GTfjA/export?format=csv&gid=0&usp=sharing"                   

##

SCOPE = ['https://spreadsheets.google.com/feeds',  'https://www.googleapis.com/auth/drive']

app = Flask(__name__)

## The default route shows a web page . It use for testing only
@app.route('/')
def index():
    return ('Flask Webhook 2021 Is Deployed successful. It is not free from bug yet')

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(silent=True)
    action = data['queryResult']['action']
    
    if action == "test_connection" :
        return test_connection(data)
    elif action == "register_participants" :
        return register_participants(data)
    elif action == "request_callback" :
        return request_callback(data)
    elif action == "check_time":
       return read_shuttlebustime(data)
    elif action == "dummy_action" :
        return funct_dummy(data)
    else:
        return handle_unknown_action(data)

########################################################################
def test_connection(data):
   response = {}
   replytext = "Hi there. You have made a successful connection to the webhook. The webhook has received your utterance <" + data['queryResult']['queryText'] + ">"
   response["fulfillmentText"] = replytext  
   return jsonify(response)  


########################################################################
def handle_unknown_action(data):
   response = {}
   replytext = "Oh dear! Your intent <" + data['queryResult']['intent']['displayName'] + "> for action <" + data['queryResult']['action']  + "> is not implemented in the webhook yet. Please disable fulfillment for the intent."
   response["fulfillmentText"] = replytext
   return jsonify(response)            
   

   
########################################################################
def register_participants(data):
   shirtsize = data['queryResult']['parameters']['shirtsize']
   name =  data['queryResult']['parameters']['person']['name']
   department = data['queryResult']['parameters']['department']

   creds = ServiceAccountCredentials.from_json_keyfile_name(KEY_FILE, SCOPE)
   client = gspread.authorize(creds)
   
   # Find a workbook by name and open the first sheet
   # Make sure you use the right name here.
   # Extract of the values

   sheet = client.open(GOOGLE_SHEET_WRITE).worksheet('registration')
   values = [name, department, shirtsize]
   sheet.append_row(values, value_input_option='RAW')

   # Prepare a response
   response = {}
   replytext = "Hi "  + name + ", Thanks for registrating for the event. We will reserve shirt size " + shirtsize + " for you. We've got your information in the spreadsheet. Please collect at HR Department. "
   response["fulfillmentText"] = replytext
   return jsonify(response)  


#######################################################################

def request_callback(data):
   phone = data['queryResult']['parameters']['phone-number']
   name =  data['queryResult']['parameters']['person']['name']
   querytext = data['queryResult']['queryText']

   creds = ServiceAccountCredentials.from_json_keyfile_name(KEY_FILE, SCOPE)
   client = gspread.authorize(creds)
   # Find a workbook by name and open the first sheet
   # Make sure you use the right name here.
   sheet = client.open(GOOGLE_SHEET_WRITE).worksheet('callback')
   # Extract and print all of the values
   values = [name, phone, querytext]
   sheet.append_row(values, value_input_option='RAW')
   # Prepare a response
   response = {}
   replytext = "Hi "  + name + ", sorry I can't help you now. But, someone will call you back at " + phone + ". Talk to you soon. We've got your information in the spreadsheet."
   response["fulfillmentText"] = replytext
   return jsonify(response)  

########################################################################

def read_shuttlebustime(data):
   pickup_pt = data['queryResult']['parameters']['pickup_pt']
   
   # download a file from Google as CSV
   # Upload into Pandas dataframe
   # Do a dataframe search based on parameter value matching col value of the dataframe
   # Pick up the required value

   df = pd.read_csv(GOOGLE_SHEET_READ_URL)
   df_selected = df[ ( df['PickupPoint'] == pickup_pt    )]
   result = df_selected[ [ 'Time'  ]].tostring(index = False)

   if search("Empty", result) :
       replytext = 'I am sorry. I am not able to find any related information'
   else:

       replytext = 'The pickup time is ' + str(result)
   # Prepare a response
   response = {}
   response["fulfillmentText"] = replytext
   return jsonify(response)  


#######################################################################

########################################################################

def funct_dummy(data):
   response = {}
   response["fulfillmentText"] = "replace with the reply text"
   return jsonify(response) 
   
   
########################################################################
   
# run Flask app
if __name__ == "__main__":
        app.run()