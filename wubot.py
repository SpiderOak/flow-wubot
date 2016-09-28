from flow import Flow
import urllib2
import json

# Fill in bot_name and wu_api_key.
bot_name = ""
wu_api_key = ""
flow = Flow(bot_name)


@flow.message
def check_message(notif_type, data):
    regular_messages = data["regularMessages"]
    for message in regular_messages:
        msg = message["text"]
        cid = message["channelId"]
        channel = flow.get_channel(cid)
        oid = channel["orgId"]
        # Parse the message
        if is_it_for_me(flow.account_id(), is_dm(channel), message):
            # I'm sure there are better ways to do this.
            try:
                msg = msg.split(": ")[1]
                msg = msg.split(", ")
                city = msg[0].replace(" ", "_")
                state = msg[1].replace(" ", "_")
                weather = get_weather(city, state)
            except:
                weather = "Unable to get weather information. Please make sure your message is formatted " \
                          "as '@%s: City, State' or 'City, Country' and check spelling." % bot_name
            # Return the weather
            flow.send_message(oid, cid, "%s" % weather)


def get_weather(city, state):
    wurl = urllib2.urlopen("http://api.wunderground.com/api/%s/geolookup/conditions/q/%s/%s.json" % (wu_api_key, state,
                                                                                                     city))
    wu_result = wurl.read()
    wu_parsed = json.loads(wu_result)
    location = wu_parsed['location']['city']
    temperature = wu_parsed['current_observation']['temp_f']
    precipitation = wu_parsed['current_observation']['precip_today_string']
    msg = "Current temperature in %s is: %s \r Precipitation today: %s " % (location, temperature, precipitation)
    return msg


def is_dm(channel):
    return len(channel['purpose']) > 0


def is_it_for_me(account_id, dm, message):
    # If it's my message, ignore it
    if message["senderAccountId"] == account_id:
        return False
    # If it's a direct message, then we care about it
    if dm:
        return True
    # Am I highlighted?
    other_data = message['otherData']
    if len(other_data) > 0:
        # dirty way ot figure out if we are being highlighted
        if account_id.lower() in other_data.lower():
            return True
    return False

# Main loop to process notifications.
print("Listening for incoming messages... (press Ctrl-C to stop)")
flow.process_notifications()