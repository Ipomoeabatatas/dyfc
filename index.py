    # /index.py

from flask import Flask, request, jsonify
import os
import json
import requests
import pandas as pd
import numpy as np
from re import search
import gspread
import datetime
import pytz

from oauth2client.service_account import ServiceAccountCredentials

### PLEASE MODIFY THE NEXT TWO LINES TO CUSTOMIZE TO YOUR OWN GOOGLESHEET ###

   
KEY_FILE = "secret-key-file.json"
GOOGLE_SHEET = "DYFC-GSheet-Backend"                   


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
    
    timeZ_Sg = pytz.timezone('Asia/Singapore')
    current_time = datetime.datetime.now(timeZ_Sg)  # use for logging purpose only

    if action == "test_connection" :
        return test_connection(data)
    elif action == "pre_register" :
        return register_participants(data)
    elif action == "request_callback" :
        return request_callback(data)
    elif action == "read_sbtime":
       return read_gs_transport(data)
    elif action == "dummy_action" :
        return funct_dummy(data)
    else:
        return handle_unknown_action(data)

########################################################################
def test_connection(data):
   timeZ_Sg = pytz.timezone('Asia/Singapore')
   current_time = datetime.datetime.now(timeZ_Sg)
   
   response = {}
   replytext = "You have made a successful connection to the webhook on " + str(current_time)
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
   shirtsize = data['queryResult']['parameters']['size']
   name =  data['queryResult']['parameters']['person']['name']
   department = data['queryResult']['parameters']['department']

   timeZ_Sg = pytz.timezone('Asia/Singapore')
   current_time = str(datetime.datetime.now(timeZ_Sg))
   
   row = [name, department, shirtsize, current_time]

   # Find a worksheet by name and open the first sheet
   creds = ServiceAccountCredentials.from_json_keyfile_name(KEY_FILE, SCOPE)
   client = gspread.authorize(creds)
   sheet = client.open(GOOGLE_SHEET).worksheet('PreRegister')
   
   sheet.append_row(row, value_input_option='RAW')

   # Prepare a response
   response = {}
   replytext = "Hi "  + name + ", Thanks for pre-registrating for the event. We will reserve shirt size " + shirtsize + " for you. We've got your information in the spreadsheet. Please collect at HR Department. "
   response["fulfillmentText"] = replytext
   return jsonify(response)  


#######################################################################

def request_callback(data):
   phone = data['queryResult']['parameters']['phone-number']
   name =  data['queryResult']['parameters']['person']['name']
   querytext = data['queryResult']['queryText']

   timeZ_Sg = pytz.timezone('Asia/Singapore')
   current_time = str(datetime.datetime.now(timeZ_Sg))

   row = [name, phone, querytext, current_time]

   creds = ServiceAccountCredentials.from_json_keyfile_name(KEY_FILE, SCOPE)
   client = gspread.authorize(creds)
   sheet = client.open(GOOGLE_SHEET).worksheet('CallbackRequest')   
   sheet.append_row(row, value_input_option='RAW')

   # Prepare a response
   response = {}
   replytext = "Hi "  + name + ", sorry I can't help you now. But, someone will call you back at " + phone + ". Talk to you soon. We've got your information in the spreadsheet."
   response["fulfillmentText"] = replytext
   return jsonify(response)  

########################################################################


########################################################################
# modified 24 Aug 2023

def read_gs_transport(data):
   pickup_pt = data['queryResult']['parameters']['dev_pickup']
   
   # download a file from Google as CSV
   # Upload into Pandas dataframe
   # Do a dataframe search based on parameter value matching col value of the dataframe
   # Pick up the required value

   creds = ServiceAccountCredentials.from_json_keyfile_name(KEY_FILE, SCOPE)
   client = gspread.authorize(creds)
   sheet = client.open(GOOGLE_SHEET).worksheet('Transport')   
   
   data = sheet.get_all_values()
   # Extract column names from the first row
   column_names = data[0]
   # Convert data to a Pandas DataFrame, excluding the first row (column names)
   df = pd.DataFrame(data[1:], columns=column_names)
    
   df_selected = df[ ( df['PickupPoint'] == pickup_pt    )]
   result = df_selected[ [ 'Time'  ]].to_string(index = False, header=False)

   if search("Empty", result) :
       replytext = 'I am very sorry. I am not able to find any related bus pickup information.'
   else:
       replytext = 'The bus will depart from ' + pickup_pt + ' at ' + str(result)
   # Prepare a response
   response = {}
   response["fulfillmentText"] = replytext
   return jsonify(response) 

########################################################################

def funct_dummy(data):
   response = {}
   response["fulfillmentText"] = "replace with the reply text"
   return jsonify(response) 
   
   
########################################################################
   
# run Flask app
if __name__ == "__main__":
        app.run()
