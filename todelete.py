@app.route('/webhook', methods=['POST'])

def webhook():
    data = request.get_json(silent=True)
    action = data['queryResult']['action']   
    if action == "request_callback" :
        return request_callback(data)
    else:
        return handle_unknown_action(data)
         
def request_callback(data):
   phone = data['queryResult']['parameters']['phone-number']
   name =  data['queryResult']['parameters']['person']['name']
   ## logic to write information to a database
   ## 
   response = {}
   replytext = "Hi "  + name + ", we will call you back at " + phone + ". Talk to you soon."
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