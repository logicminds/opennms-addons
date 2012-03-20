#!/usr/bin/env python
import urllib
from xml.dom import minidom
import sys
import re
import subprocess
import os

'''
    Author: Corey Osman
    Email: corey@logicminds.biz
    Date: 2-26-2010
    Purpose: get the local weather from a zip or airport code that is defined in the dict and return to opennms as an event
    Usage: getWeather.py 30067 or getWeather.py ATL
    Update: 3-19-2012
         Fixes: better error handling while parsing data and calling the send event script
'''

# Set the path of your send-event.pl otherwise leave the default value
SEND_EVENT='/opt/opennms/bin/send-event.pl'
# Set the hostname or ip of your opennms server, localhost is the default if running this script on the server
NMS_HOST='localhost'
# The following is the api code you need to get from weatherbug
# http://weather.weatherbug.com/desktop-weather/api.html
API_CODE = 'A6585716893'
# This is the url to get the severe weather alert the zip code will be appended later
# Don't Change the following url 
WEATHER_URL = 'http://%s.api.wxbug.net/getAlertsRSS.aspx?ACode=%s&OutputType=1&zipCode=%s'
# This contains the namespace of the xml code we get from weatherbug
WEATHER_NS = 'http://www.aws.com/aws'
# Extreme words are used to create new types of events which must be defined in the Weather.events.xml file or similar
# Basically I use these words to scan the weather text for keywords.  If any of these words are in the text the weather is marked
# extreme and a new UEI is created.
EXTREMEWORDS=['hurricane', 'tornado', 'blizzard']

# The Following list is for a simple lookup if you can't remember zip codes
# If you add more zip codes here they will be included with the --all command
AIRPORT_CODES={'ATL': '30297', 'BWI': '21075', 'BOS': '02081', 'ORD': '60018', 
'CVG': '41048', 'TEX': '75050', 'DEN': '80216', 'IND': '46241', 'SFO': '94587',
'SEA': '90002', 'PDX': '90210'}

# Add more extreme words to the following list to trigger new events
# These events will need to be defined in the Weather.events.xml file
extremewords=['hurricane', 'tornado', 'blizzard']

# Test: 'http://A6585716893.api.wxbug.net/getAlertsRSS.aspx?ACode=A6585716893&OutputType=1&zipCode=90210'

def make_pretty(data):
    '''
    This func will make the text appear more pleaseing to the eye for opennms
    Input: string of weather data
    Output: list of affected counties and weather alert
    '''
    # Add a space between the commas so the words can be wrapped correctly in the browser
    data = data.replace(',',', ')
    # Separate affected areas 
    return data

def find_county(zip):
    '''
    Input: a zip code 
    Output: the county name in which the zip code belongs to
    '''
    # I need to find a online server to lookup this info up. 
    # Once this is done I find out if the city,state and other location information
    pass

def parsealert(datalist):   
    '''
    Pass a list of dicts of raw data and filter out the affected counties, and alert
    We can find the counties by searching for ALL CAPS followed by mixed case, followed by ALL CAPS
    Output: return a similar list of dicts but with added key/values
    '''
     
    weatherdata = []
    # loop through each dict of data in alert list
    for data in datalist:
        # Separtate alert from counties and adjent words
        strlist = re.split('\:\s', data.get('aws:msg-summary'), maxsplit=1)
        data['summary'] = strlist[0]
        # Separate the counties and condition
        # It appears the NWS reports different strings everytime which is diffictult to parse
        try:
            strlist2 = re.split('\-\s\-?', strlist[1], maxsplit=1)
            # Do this if the condition doesn't exist
            if len(strlist2) == 2:
                data['counties'] = strlist2[0]
                data['condition'] = strlist2[1]
            else:
                data['counties'] = strlist[1]
                data['condition'] = ""
        except:
            #print "Warning: no county or condition information exists"
            data['counties'] = ""
            data['condition'] = ""

        # Lets find out if the weather is extreme by searching for specific words
        for word in EXTREMEWORDS:
            try:
                # If the alert or condition contains one of the extreme words mark as extreme
                if re.search(word, data.get('condition') + data.get('summary'), re.IGNORECASE ):
                    data['extreme'] = True
                    data['extremetype'] = word + 'Alert'
                else:
                    data['extreme'] = False
                    data['extremetype'] = None
            except:
                None
                
        weatherdata.append(data)

    return weatherdata


def get_node_data(dom, fields):
    '''
    Input: a dom object tree
    Output: a list of dicts with the fields and values
    '''
    # this is only here to remind me what xml tags I need to get
    #alert = {'aws:title': None, 'aws:type': None, 'aws:posted-date': None, 'expiresdate':None, 'aws:msg-summary':None }
    datalist = []
    # Get the field
    
    for field in fields:
        i = 0  # reset the counter so the dict is populated properely
        for node in dom.getElementsByTagName(field):
            # If nothing exist in the node, goto next node or field
            if hasattr(node.firstChild, "wholeText"):
                value = make_pretty(node.firstChild.wholeText)
            else:
                value = None
            # If nothing exists we need to create
            if len(datalist) < i+1:
                # append and create the dict
                datalist.append({})
                
            # asssign the value to the field in the list
            datalist[i][field] = value
           
            # increment number so we can refer to each element
            i +=1
    datalist = parsealert(datalist) 
    return datalist

def weather_for_zip(zip_code):
    '''
    Input: send a zipcode
    Output: a list of dicts that contain various types of information gathered from the resulting xml weather data from weatherbug
    A list is returned since weather data may contain multiple alerts for different times, areas or event types of weather.
    '''
    # append the zipcode to the weather url
   
    url = WEATHER_URL % (API_CODE, API_CODE, zip_code)
    alerts = []
    # These are the fields we want to get
    fields = ['aws:title', 'aws:type', 'aws:posted-date', 'aws:msg-summary']
    dom = minidom.parse(urllib.urlopen(url))
    # get the data and return a list of dicts
    alerts = get_node_data(dom, fields)
    # We need to parse the data from the summary out to find specific conditions
    alerts = parsealert(alerts)
    return alerts

def send_to_opennms(alerts, loc):
    '''
    Send the weather message and the source of the location to the send-alert.pl command
    to create an alert that opennms can act upon

    Ex: send-event.pl uei.opennms.org/vendor/weather/events/WeatherAlert --parm 'alertmsg Its raining really hard' --parm 'loc BOS'

    '''
    
    uei='uei.opennms.org/vendor/weather/events/WeatherAlert'
    # Send different types of alerts based on weather condition
    if not os.path.isfile(SEND_EVENT):
        print "%s file not found" % SEND_EVENT
        return None
    
    for alert in alerts:
        # If this is an event that is "extreme" defined by the extreme words list then lets make a new weather event type.
        # This will give us the ability to have a more refined event that can be filtered or alerted more easily.  
        if alert.get('extreme'):
            uei='uei.opennms.org/vendor/weather/events/%s' % (alert.get('extremetype'))

        pargs='%s %s %s --parm \'alertmsg %s\' --parm \'loc %s\' --parm \'type %s\' --parm \'title %s\' --parm \'summary %s\' --parm \'counties %s\'' % (SEND_EVENT,uei, NMS_HOST, alert.get('condition'), loc, alert.get('aws:type'), alert.get('aws:title'), alert.get('summary'), alert.get('counties'))

        subprocess.Popen(pargs, stdout=subprocess.PIPE, shell=True)
        print "%s : %s" % (loc, alert.get('aws:title'))
        # Uncomment the break to process multiple weather alerts from one area
        #break

def alert_by_zip(zipcode):
    alerts = weather_for_zip(zipcode)
    if alerts:
        send_to_opennms(alerts, zipcode)
    else:
        print "No weather to report for %s" % zipcode

def alert_by_airport(aircode):
    alerts = weather_for_zip(AIRPORT_CODES[aircode])
    if alerts:
       send_to_opennms(alerts, aircode)
    else:
        print "No weather to report %s" % aircode
                     


# Call the weather function and pass in the zip code with via the command line
if len(sys.argv) is 2:
    # check to see if the zip code is valid
    if re.match('\d{5,5}',sys.argv[1]):
        alert_by_zip(sys.argv[1])

    # If you want to report lots of weather alerts you can iterate over all the airport codes
    elif sys.argv[1] == '--all':
        for key in AIRPORT_CODES.iterkeys():
            print "Checking weather in %s " % key
            alert_by_airport(key)

     # check to see if the airport code is valid and is in the airport_codes dictionary
    else:
        if re.match('[A-Z]{3,3}', sys.argv[1]) and AIRPORT_CODES.get(sys.argv[1]):
            alert_by_airport(sys.argv[1])
        else:
            print 'Airport code %s is not in the list' % sys.argv[1]

else:
    print 'no zipcode was given'
    print 'Usage: python /opt/opennms/bin/getWeather.py 90210'
