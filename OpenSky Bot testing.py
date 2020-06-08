#Import Modules
from opensky_api import OpenSkyApi
from geopy.geocoders import Nominatim
import json
import time
from colorama import Fore, Back, Style 
#Various imports for output
from pushbullet import Pushbullet
pb = Pushbullet("***REMOVED***")

geolocator = Nominatim(user_agent="OpenSkyBot", timeout=5)
api = OpenSkyApi("", "")

#Set Plane ICAO
TRACK_PLANE = 'a4c79b'

#Pre Set Variables
geo_altitude = None
feeding = None
last_feeding = None   
#Begin Looping program
while True:
#Preset reseting variables
    invalid_Location = None
    longitude = None
    latitude = None
#Get API States for Plane
    planeData = api.get_states(icao24=TRACK_PLANE)
    print (Fore.YELLOW)
    print ("OpenSky Debug", planeData)
    print(Style.RESET_ALL) 

#Pull Variables from planeData
    if (planeData != None):
        for dataStates in planeData.states:
            longitude = (dataStates.longitude)
            latitude = (dataStates.latitude)
            on_ground = (dataStates.on_ground)
            geo_altitude = (dataStates.geo_altitude)
            
            print (Fore.BLUE)
            print ("On Ground: ", on_ground)
            print ("Latitude: ", latitude)
            print ("Longitude: ", longitude)
            print ("GEO Alitude: ", geo_altitude)
        
            
    #Lookup Location of coordinates 
        if not((longitude == None) and (latitude == None)):

            combined = f"{latitude}, {longitude}"
            location = geolocator.reverse(combined)
            print (Fore.YELLOW)
            print ("Geopy debug: ", location.raw)
            print(Style.RESET_ALL) 
            feeding = True 
        else:
            print (Fore.RED + 'Not Feeding Location')
            feeding = False
            print(Style.RESET_ALL) 
        print ("Feeding: ", feeding)
    #Figure if valid location, valid being geopy finds a location
        if feeding:
            try:
                geoError = location.raw['error']
            except KeyError:
                invalid_Location = False
                geoError = None
            else:
                invalid_Location = True
        
        
    
        if invalid_Location:
            print (Fore.RED)
            print ("Invalid Location: ", invalid_Location)
            print (geoError)
            print ("Likely Over Water or Invalid Location")
            print(Style.RESET_ALL)
            

    #Convert Full address to sep variables
        elif feeding:
            address = location.raw['address']
            country = address.get('country', '')
            state = address.get('state', '')
            county = address.get('county', '')
            city = address.get('city', '')
            
            
            print (Fore.YELLOW)
            print ("Address Fields debug: ", address)
            print(Style.RESET_ALL)
            print (Fore.GREEN)
            print("Entire Address: ", location.address)
            print ()
            print ("Country: ", country)
            print ("State: ", state)
            print ("City: ", city)
            print ("County: ", county)
            print(Style.RESET_ALL)



        #Check if tookoff
        tookoff = bool(last_feeding is False and feeding and on_ground is False and invalid_Location is False and geo_altitude < 10000)
        print ("Tookoff Just Now:", tookoff)

        #Check if Landed
        landed = bool((last_feeding and feeding is False and invalid_Location is False and last_geo_altitude < 10000) or (on_ground and last_on_ground is False))
        print ("Landed Just Now:", landed)
        





    #Takeoff Notifcation and Landed
        if tookoff:
            tookoff_message = ("Just took off from" + " " + city + ", " + state + ", " + country)
            print (tookoff_message)
            push = pb.push_note("Elon's Jet", tookoff_message)


        if landed:
            landed_message = ("Landed just now at" + " " + city + ", " + state + ", " + country)
            print (landed_message)
            push = pb.push_note("Elon's Jet", landed_message)
   

        last_feeding = feeding
        last_geo_altitude = geo_altitude
        last_on_ground = on_ground
    else:
        print ("Rechecking OpenSky")
        planeDataMSG = str(planeData)
        push = pb.push_note("Rechecking OpenSky, OpenSky Debug->", planeDataMSG)

    print (Back.MAGENTA, "--------------------------------------------------------------------")
    print(Style.RESET_ALL)
    time.sleep(15)