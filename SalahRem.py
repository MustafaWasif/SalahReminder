import smtplib  # secure email
import socket  # catching errors
import sys  # exit func
from email.mime.text import MIMEText
import os # To hide password and/or secret keys
#from validate_email import validate_email
from datetime import datetime  # find day and time
import time
#from Turn import *
import geopy.geocoders
from geopy import geocoders

from pytz import timezone
import json
import requests
#-----import geograpy
#-----import nltk
import pycountry # all countries
import geonamescache # all cities
import sqlalchemy # DB
from datetime import timedelta


from flask import Flask, jsonify, render_template, request, redirect, url_for, session
# Create an instance of the app
app = Flask(__name__)
app.secret_key = "abc"
#app.permanent_session_lifetime = timedelta(days=7)

#prayers = ["Fajr", "Zuhr", "Asr", "Maghrib", "Isha"]

#Dictionary
Prayers = {
    "Fajr": [4, 0],    # 4:00 AM
    "Zuhr": [12, 30],  # 12:30 PM
    "Asr": [15, 5],    # 3:05 PM
    "Maghrib": [18, 0], # 6:00 PM
    "Isha": [20, 20]   # 8:20 PM
}
print (Prayers)

#------------------------------------------------------------------#
                  # API Functionality (Aladhan)
def api_function(cityName, countryName):
    global Prayers
    response = requests.get("http://api.aladhan.com/v1/timingsByCity?city="+cityName+"&country="+countryName+"&method=4")
    #print(response.json()['data']['timings'])

    #print("This is", a["data"]["timings"])
    if (response.status_code) == 200:
        a = json.loads(response.content)
        # Go inside dict 'a' into data.timings and iterate over the key-value pairs inside
        for key, value in a["data"]["timings"].items():
            # Extracting prayer name
            api_prayer = "{}".format(key) 

            # Extracting prayer time (minute & hour)
            api_time = "{}".format(value) # api_time is a string
            api_time = api_time.split(":") # api_time is a list now containing 2 strings
            api_hour, api_minute = api_time[0], api_time[1]

            # Storing in the local dict 'Prayers'
            if (api_prayer == "Fajr"):
                Prayers["Fajr"][0], Prayers["Fajr"][1] = api_hour, api_minute
            elif (api_prayer == "Dhuhr"):
                Prayers["Zuhr"][0], Prayers["Zuhr"][1] = api_hour, api_minute
            elif (api_prayer == "Asr"):
                Prayers["Asr"][0], Prayers["Asr"][1] = api_hour, api_minute
            elif (api_prayer == "Maghrib"):
                Prayers["Maghrib"][0], Prayers["Maghrib"][1] = api_hour, api_minute
            elif (api_prayer == "Isha"):
                Prayers["Isha"][0], Prayers["Isha"][1] = api_hour, api_minute
                #print(Prayers)

            #print("{} == {}".format(key, value))
        #print(json.loads(response.content.decode('utf-8'))) response.json['data']['timings']
    else:
        print("Bad request", response.status_code)
        Prayers = Prayers.clear()

    print ("After----\n",Prayers)
#------------------------------------------------------------------#
#print ("After----\n",Prayers)
"""
print("Enter city and country names to get prayer times notification based on that area.")
print("City Name:")
cityName = input()
print("Country Name:")
countryName = input()
"""

cityName = ""
countryName = ""
#api_function(cityName, countryName)
#api_function("Victoria", "Canada")



# Email Declarations
smtp_server = 'smtp.gmail.com'
port = 587  # 587 is the secure connection google listens to.

sender = os.environ.get("EMAIL_SENDER")
password = os.environ.get("EMAIL_KEY") #use when running on other servers
email_title = 'Salah Reminder'
recipient = "" # os.environ.get("EMAIL_RECIPIENT")
message = "Salatul fajr in   minutes."

#----------------------- Function alert -> sends email notification 10 minutes prior to salah
def alert(sender, password, email_title, recipient, message):

    try:
        message = MIMEText(message)
        message['Subject'] = email_title
        message['From'] = sender  # 'ergruguvic@gmail.com'
        message['To'] = recipient

        print("Starting...")

        # create smtp session
        server = smtplib.SMTP(smtp_server, port)
        print("MW1")
        # Identifies your computer to server, check TLS support, queries what extensions available
        server.ehlo()
        # encrypt, TLS(Transport Layer Security)
        server.starttls()

        server.ehlo()
        # Login to server
        print("MW2")
        server.login(sender, password)
        print(message.as_string())

        # Sending email
        print("Sending Email...")
        server.sendmail(sender, recipient, message.__str__())
        #print("Current msg = ", message)
        print("Email Sent!")

    except (socket.gaierror, socket.error, socket.herror, smtplib.SMTPException) as e:
        print("Failed to send email!")
        print(e)
        sys.exit(1)

    finally:
        # End server
        server.close()

def findLocalTime(cityName, countryName):
    #global cityName, countryName
    error_msg = None
    if(not(cityName and cityName.strip()) or not(countryName and countryName.strip())):
        error_msg = "No city name and country name found"
        print("Search for LocalTime", error_msg)
        return error_msg
    else:
        geoname_account = geopy.geocoders.GeoNames(username = "mustafa12", timeout = 100)
        location = geoname_account.geocode(cityName+", "+countryName) # cityName+", "+countryName
        try:
            local_tz = geoname_account.reverse_timezone(location.point)
            print(cityName, countryName, local_tz)
            local_time = timezone(str(local_tz))
            #current_Time = datetime.now(local_time)
        except:
            error_msg = "Invalid country and/or city"
            print("Search for LocalTime", error_msg)
            return render_template("signup.html", error = error_msg)   
    return(local_time)

#findLocalTime(cityName, countryName)

#current_Time = datetime.now(findLocalTime(cityName, countryName))
#print(current_Time)
#current_Time = current_Time.strftime("%H:%M")

#current_Hour = datetime.now().strftime("%H")
#currentHour_int = int(current_Hour)

#current_Minute = datetime.now().strftime("%M")
#currentMinute_int = int(current_Minute)



prayerHourDiffList = []
sortedList = []
"""
# Get Salah name (key) from salah hour (value)
def getKey(value):
    for key, val in Prayers.items():
        print(value, Prayers[key][0])
        if(value == Prayers[key][0]):
            #print("MW!")
            print(key)
            return key 
    return "Invalid value/value not present in dictionary"
"""


# Removes characters such as "(", ",", ")" from the string to make it output ready and converts string to json string
def remove_extra_char(a_tuple):
    print("tuple version:", a_tuple)
    tuple_to_string = str(a_tuple)
    print("String version:", tuple_to_string)
    characters_to_remove = "(,')" # For correct output in webpage w/o these characters
    for character in characters_to_remove:
        tuple_to_string = tuple_to_string.replace(character, "")
        #print(tuple_to_string)
    
    #print(tuple_to_string)
    new_string = tuple_to_string.strip(")'")

    #new_string = new_string.replace(". ", '\n')
    #new_string = json.dumps(original_string) # converts string to json string
    return new_string

# Checks if any structure (tuple, list, dict) is empty or not - Will be needed to check tuple 'past_prayer_msg' is empty or not
def isEmpty(structure):
    if(structure):
        # There is content inside, so not empty. Therefore false
        return False
    else:
        return True

# To be able to return multiple json string on webpage
def MergeTupleConvertString(tuple1, tuple2):
    mergedTuple = tuple1 + tuple2
    mergedTuple_to_string = str(mergedTuple)
    return mergedTuple_to_string



minDiff = 24 #Closest prayer hour from current hour 
SetPrayer = "default" #Next prayer; Eg- Current time: 1AM, SetPrayer would be Fajr, UpcomingPrayer would be Zuhr
pastPrayer = "" #Previous prayer
UpcomingPrayer = "" #Next next Prayer (Prayer that comes after SetPrayer)
count = 0
switch = 1
characters_to_remove = "(')" # For correct output in webpage w/o these characters
past_prayer_msg = () # Empty Tuple (Contains past prayer msg if applicable)
button = 0 # Needed for tracking past prayer record condition
button_store = []

# MAIN for loop
def Programhead(currentHour_int, currentMinute_int):
    global minDiff, SetPrayer, pastPrayer, UpcomingPrayer, count, past_prayer_msg 
    global button, button_store
    for prayer in Prayers:
        #switch = 1
        count += 1 # count: To keep count of no. of cycles in the for loop.
        #print("This is count:", count)
        prayerHour = Prayers[prayer][0] #Prayer time in hour (Accessing Dictionary, (Prayers[]), then fetching 1st item from array, (prayer[0]), which is in the Dictionary)
        prayerMins = Prayers[prayer][1] #prayer time in minutes

        prayerHour = int(prayerHour)
        prayerMins = int(prayerMins)
        #print(prayerHour)

        difference = prayerHour - currentHour_int
        difference_mins = prayerMins - currentMinute_int
        #print("difference in hours:", difference)
        prayerName = prayer # prayerName: name of the prayer in the current loop
        #print(prayer)
        
        if(difference_mins < 0 and difference != 0):
            difference = difference - 1  #Subtract 1 for correct hour countdown measure. If Hour difference is already zero, don't subtract! Also when hour diff is < 0, it gives accurate hour diff countdown with diff mins < 0
        
        # Keeping record of past prayer upto 30 minutes after prayer time due. Final reminder can be set (maybe?).
        """
        secondary_diff_hrs = prayerHour - currentHour_int
        if(prayerMins > currentMinute_int): # eg- prayer time = 1:50 & current time = 2:10 (condition applicable for hour difference of -1)
                secondary_diff_mins = (60 - prayerMins) + currentMinute_int # eg- (60 - 50) + 10 = 20 minutes difference
        else:
            secondary_diff_mins = prayerMins - currentMinute_int # all negative values
        """
        if ((prayerHour == currentHour_int and difference_mins < 0) or difference == -1):
            secondary_diff_hrs = prayerHour - currentHour_int # either 0 or -1
            pastPrayer = prayerName
            print("----------------", pastPrayer, SetPrayer)
            if(prayerMins > currentMinute_int): # eg- prayer time = 1:50 & current time = 2:10 (condition applicable for hour difference of -1)
                secondary_diff_mins = (60 - prayerMins) + currentMinute_int # eg- (60 - 50) + 10 = 20 minutes difference
            else:
                secondary_diff_mins = prayerMins - currentMinute_int # all negative values
            
            while(True):
                if(secondary_diff_hrs == -1 and secondary_diff_mins <= 0): #eg- 1:30 & 2:31
                    button = 0
                    print("Trap condition: More than 30 minutes past pastPrayer, so no more reminders. button made 0")
                    break;
                elif(secondary_diff_hrs == 0 and secondary_diff_mins > 0): # Prayer hour but not prayer time. Eg- current time: 1:10, Prayer time: 1:25 
                    print("Another trap: Few more minutes until prayer/SetPrayer time. So not yet a pastPrayer reminder. Soon will be. button made 0")
                    break;
                else:
                    # Check if difference in minutes is within 30 minutes or not. 
                    if (abs(secondary_diff_mins) > 1 and abs(secondary_diff_mins) < 30):
                        #print(pastPrayer)
                        #print(pastPrayer, "time ending soon! Please Pray if you haven't already.")
                        print(abs(secondary_diff_mins), "minutes past", pastPrayer,". Please Pray if you have not already.") #return
                        past_prayer_msg = abs(secondary_diff_mins), "minutes past", pastPrayer+". Please Pray if you have not already."
                        button = 1
                        #print(type(past_prayer_msg[0]))
                        break;
                    elif(abs(secondary_diff_mins) == 30):
                        button = 0
                        past_prayer_msg = () # Empty the dictionary to display correct return statement from below. Otherwise last updated past_prayer_msg keeps on poppin on screen.
                        message = pastPrayer+ " time ending soon! Please Pray if you haven't already."
                        alert(sender, password, email_title, recipient, message)
                        print(message)
                        break;
                    else:
                        button = 0
                        past_prayer_msg = () # Empty the dictionary to display correct return statement from below. Otherwise last updated past_prayer_msg keeps on poppin on screen.
                        # Discard if difference in minutes > 30
                        print("-1 <= secondary_diff_mins < 0 or < -30 or > 30", secondary_diff_mins)
                        break;
        else:
            button = 0
        
        button_store.append(button)
        """
        Creates Problem: Empties past_prayer_msg when goes to next prayerName in the main for loop
        Why needed: When form submitted with country and city that has past_prayer_msg, after re-submitting form with different country and city, past_prayer_msg stays.
        Solution: When form "Setup Reminder" button clicked
        else:
            print("Did not go to record past prayer")
            past_prayer_msg = () # Empty the dictionary to display correct return statement from below. Otherwise last updated past_prayer_msg keeps on poppin on screen.
        """
        #--------- End of code for Keeping record of last prayer ----------------------------------

        # For long past prayer times (in hours) of current day 
        if (difference < 0): 
            difference += 24

        # When current time has just passed the prayer time and variable 'difference' is 0.
        # Condition: When difference in hour = 0, but 59 more minutes until prayer time.
        # Eg - Current Time= 13:50 & Prayer Time= 14:49. difference_mins will be negative from 13:50 to 13:59. 
        # Prev condition: if (difference == 0 and difference_mins < 0):
        
        #if (prayerHour == currentHour_int and difference_mins == 0):
            #print("jabita")
            #difference += 24
        #elif
        if (prayerHour == currentHour_int and difference_mins < 0): # Eg- Current Time= 2:30 & Prayer Time= 2:20.
            
            difference += 23

        if(count == 6):
            count = 1
            minDiff = 24
        print("count:", count)

        #if(difference_mins > 0):
        # To set SetPrayer and UpcomingPrayer in the first while loop cycle, i.e 5 cycles in for loop. 2nd iteration of while loop sets incorrect UpcomingPrayer
        if(count <= 5):
            #print("Prayer Name:", prayerName)
            #print("difference:", difference, "minDiff:", minDiff)
            """
            if(SetPrayer == "Isha" and prayerName == "Fajr"): # To allow new rotation for new day.
                print("minDiff at the end of day (after Isha)", minDiff)
                minDiff = 24
            """
            # Assigns setPrayer (next prayer) and UpcomingPrayer (next next prayer) 
            if difference <= minDiff:
                UpcomingMin = minDiff
                minDiff = difference
                #minPrayerHour = prayerHour # Storing the number to help in if condition later (check minPrayerHour condition)
                UpcomingPrayer = SetPrayer
                SetPrayer = prayerName
                #print("Set", SetPrayer, "\nInside if - difference:", difference, "minDiff:", minDiff)
                #print("1st if - Name of upc:", UpcomingPrayer)
            elif(difference < UpcomingMin):
                UpcomingMin = difference
                UpcomingPrayer = prayerName
                #print("Name of upc:", UpcomingPrayer)

        prayerHourDiffList.append(difference)
        sortedList.append(difference)
    #end for loop
    print("This is button Store", button_store)
    if(1 not in button_store):
        past_prayer_msg = ()
    button_store.clear()

    return (minDiff, SetPrayer, UpcomingMin, UpcomingPrayer, past_prayer_msg, difference, count)



@app.route("/")
def index():
    return redirect(url_for("signup"))

get_recipient, get_cityName, get_countryName = "", "", ""
@app.route("/signup", methods=['GET', 'POST'])
def signup(): 
    global cityName, countryName, recipient, get_recipient, get_cityName, get_countryName
    error_msg = None
    if(request.method == 'POST'):
        #session.permanent = True
        print("POSTING")
        get_recipient = request.form['email']
        #print("Recipient before signup", recipient)
        #recipient = get_recipient
        #print("Recipient after signup", recipient)
        session["email"] = request.form['email']
        try:
            get_cityName = request.form["city"]
            get_countryName = request.form["country"]

            # Validate country
            for x in pycountry.countries:
                
                #print("Inside for", x.name)
                if(get_countryName.title() == x.name):
                    #print("Inside ifff", x.name)
                    error_msg = None
                    #api_function(get_cityName, get_countryName)
                    print("Inside ifff", get_cityName, get_countryName)
                    break;
                
                # Checking the last country in the database Pycountry 
                elif(x.name == "Zimbabwe" and get_countryName.title() != "Zimbabwe"):
                    error_msg = "Unknown country! Please provide valid country name in full form (no acronyms please)."
                    return render_template("signup.html", error_msg = error_msg)
            print("-----------------------------------------")
            #Validate city
            gc = geonamescache.GeonamesCache()
            cities = gc.get_cities()
            for c in cities:
                if(get_cityName.title() == cities[c]['name']):
                    #print("Inside ifff", cities[c]['name'])
                    error_msg = None
                    #api_function(get_cityName, get_countryName)
                    print("Inside ifff", get_cityName, get_countryName)
                    break;
                # Checking the last city name listed in the Pycountry database   
                elif(cities[c]['name'] == "Chitungwiza" and get_cityName.title() != "Chitungwiza"):
                    error_msg = "Unknown city! Please provide valid city name in full form (no acronyms please)."
                    return render_template("signup.html", error_msg = error_msg)

            api_function(get_cityName, get_countryName)
        except:
            error_msg = "Exception: Please input valid city and country names"
            return render_template("signup.html", error_msg = error_msg)
        """
        try:
            get_recipient = request.form['email']
            welcome_message = "Thank you for signing up for Salah Notification"
            alert(sender, password, email_title, request.form['email'], welcome_message)
        except:
            error_msg = "Please check your email input"
            return render_template("signup.html", error_msg = error_msg)
        """
        return redirect(url_for("home"))
        
    else:
        print("GET methodxx")
        """
        if "email" in session:
            print("GET methodxx222", session)
            return redirect(url_for("home"))
        """
    return render_template("signup.html", error_msg = error_msg)

@app.route("/home")
def home():
    global get_cityName, get_countryName, get_recipient
    display_store = []
    error_msg = None

    if "email" in session:
        print("Session here", session)
        get_recipient1 = session['email']
    else:
        print("No session, so redirecting to signup")
        return redirect(url_for("signup"))
    #if(len(get_cityName) != 0 and len(get_countryName) != 0 and len(get_recipient) != 0):
    # Needed if users type "mwk.pythonanywhere.com/home" url directly. 
    if(not(get_cityName and get_cityName.strip()) or not(get_countryName and get_countryName.strip())):
        #return render_template('refresh.html')
        display_store = [] # Empty the display info for safe practice
        error_msg = "Please signup properly first"
    else:
        error_msg = None
        display_countryName, display_cityName = get_countryName, get_cityName
        display_recipient = get_recipient1
        display_store = [display_countryName, display_cityName, display_recipient]
        return render_template('refresh.html', display = display_store, error=error_msg)

    # return for if condition  
    return render_template("refresh.html", error=error_msg)

@app.route("/logout")
def logout():
    session.pop("email", None)
    return redirect(url_for("signup"))

@app.route("/_stuff")
# minDiff, SetPrayer, pastPrayer, UpcomingPrayer, count, past_prayer_msg
def findNearestDifference():
    global switch, recipient, get_recipient
    global cityName, countryName, get_cityName, get_countryName
    global characters_to_remove, isEmpty
    #global MergeTupleConvertString
    recipient = get_recipient
    cityName = get_cityName
    countryName = get_countryName
    print("This is rec:", recipient, cityName, countryName)
    LocalTime = findLocalTime(cityName, countryName)
    print("Inside main function", cityName, countryName)
    while(1):
        try:
            current_Hour = datetime.now(LocalTime).strftime("%H")
            currentHour_int = int(current_Hour)
            print(currentHour_int, LocalTime)

            current_Minute = datetime.now(LocalTime).strftime("%M")
            currentMinute_int = int(current_Minute)
            #print("This is:",currentMinute_int)

            # Call api to update next days prayer times 
            if(currentHour_int == 0 and currentMinute_int == 0): #12AM 
                print("API CALL FOR NEXT DAY")
                api_function(cityName, countryName)

            result = Programhead(currentHour_int, currentMinute_int)
            print("This is result", result)
            minDiff, SetPrayer = result[0], result[1]
            UpcomingMin, UpcomingPrayer, past_prayer_msg = result[2], result[3], result[4]  
            difference, count = result[5], result[6]
            
            #switch = 0
            #print(prayerHourDiffList)
            # ---------------------------Added due to 
            #Declarations(int(Prayers[SetPrayer][0]), int(Prayers[SetPrayer][1]), currentMinute_int, int(Prayers[UpcomingPrayer][1]))
                
            # More Declarations
            Nearest_hrs = int(Prayers[SetPrayer][0]) # Nearest Prayer time (in hour from current time)
            Nearest_mins = int(Prayers[SetPrayer][1]) # Nearest Prayer time (in minute from current time) 
            Nearest_mins_diff = Nearest_mins - currentMinute_int
            
            # Nearest_hrs_diff is equal to minDiff.
            Nearest_hrs_diff = Nearest_hrs - currentHour_int # Should be positive unless its next day (fajr) prayer
            #print(Nearest_mins_diff)

            if(Nearest_mins_diff < 0 and Nearest_hrs_diff != 0):
                Nearest_hrs_diff = Nearest_hrs_diff - 1  #Subtract 1 for correct hour countdown measure. If Hour difference is already zero, don't subtract! 
            if (Nearest_hrs_diff < 0):
                Nearest_hrs_diff += 24
            
            NearestUpcoming_min_diff_hrs = int(Prayers[UpcomingPrayer][0]) - currentHour_int
            NearestUpcoming_min_diff_minutes = int(Prayers[UpcomingPrayer][1]) - currentMinute_int

            if(NearestUpcoming_min_diff_minutes < 0 and NearestUpcoming_min_diff_hrs != 0):
                NearestUpcoming_min_diff_hrs = NearestUpcoming_min_diff_hrs - 1  #Subtract 1 for correct hour countdown measure. If Hour difference is already zero, don't subtract! 
            
            #  NearestUpcoming_min_diff_hrs becomes negative when setPrayer is Isha and upcomingPrayer is Fajr. hour difference for upcoming becomes negative. 
            if (NearestUpcoming_min_diff_hrs < 0):
                #print("Check and note timings")
                NearestUpcoming_min_diff_hrs += 24

            if (NearestUpcoming_min_diff_minutes < 0):
                NearestUpcoming_min_diff_minutes += 60
                
            # To print digital time
            if(int(Prayers[UpcomingPrayer][0]) > 12):
                digitalTime = int(Prayers[UpcomingPrayer][0]) - 12
            else:
                digitalTime = int(Prayers[UpcomingPrayer][0])

            print("minDiff:"+str(minDiff), "Nearest_hrs_diff:"+str(Nearest_hrs_diff),"difference:"+str(difference), "\nNearestminDiff:"+str(Nearest_mins_diff), "Nearest_hrs:"+str(Nearest_hrs), "currentHour_int:"+str(currentHour_int), "currentMinute_int:"+str(currentMinute_int), "Nearest_mins:"+str(Nearest_mins))
            print("NearestUpcoming_min_diff_hrs:", NearestUpcoming_min_diff_hrs, "NearestUpcoming_min_diff_minutes:", NearestUpcoming_min_diff_minutes)
            
            # Will be used for sending msg about next upcoming Salah within the day. Include actual time + countdown
            if(currentHour_int < Nearest_hrs):
                if(currentMinute_int < Nearest_mins):
                    if(Nearest_hrs_diff == 0):
                        print(Nearest_mins_diff, "minutes more until", SetPrayer, "time.") #return
                        
                        test = Nearest_mins_diff, "minutes more until", SetPrayer, "time.#"
                        #original_string = str(test)
                        new_string = remove_extra_char(test)
                        print("MW1: Doesn't make sense because of inner if statement. Note timings")
                        if(isEmpty(past_prayer_msg)):
                            return new_string
                        else:
                            # Alternative (For json string output)
                            #resultant_string = MergeTupleConvertString(test, past_prayer_msg)
                            #new_string = remove_extra_char(resultant_string)

                            past_prayer_msg = remove_extra_char(past_prayer_msg)
                            return new_string + past_prayer_msg
        
                    else:
                        #msg = str(Nearest_hrs_diff)+" hours "+ str(Nearest_mins_diff)+ " minutes more until " + str(SetPrayer)+ " time."
                        print(Nearest_hrs_diff,"hours", Nearest_mins_diff, "minutes more until", SetPrayer, "time.") #return
                        
                        test = Nearest_hrs_diff,"hours", Nearest_mins_diff, "minutes more until", SetPrayer, "time.#"
                        #return render_template('refresh.html', msg=msg)
                        #original_string = str(test)
                        new_string = remove_extra_char(test)
                        print("MW2")
                        if(isEmpty(past_prayer_msg)):
                            return new_string
                        else:
                            #resultant_string = MergeTupleConvertString(test, past_prayer_msg)
                            #new_string = remove_extra_char(resultant_string)
                            past_prayer_msg = remove_extra_char(past_prayer_msg)
                            return new_string + past_prayer_msg
                    
                    #print(minDiff,"hours", Nearest_mins_diff, "minutes more until", SetPrayer, "time.")
                    print("After ret, before tim.sleep")
                    time.sleep(60)
                elif(currentMinute_int > Nearest_mins):
                    newDiff_mins = 60 + Nearest_mins_diff #Add 60 to diff_mins to find the correct remaining minutes (newDiff_mins variable can be changed to "diff_mins" if too many different variables to incorporate in variable "message")
                    if(Nearest_hrs_diff == 0): # Eg- Current Time: 1:30, Prayer Time: 2:20
                        print(newDiff_mins, "minutes more until", SetPrayer, "time.") #return
                        
                        test = newDiff_mins, "minutes more until", SetPrayer, "time.#"
                        #original_string = str(test)
                        new_string = remove_extra_char(test)
                        print("MW3")
                        if(isEmpty(past_prayer_msg)):
                            return new_string
                        else:
                            #resultant_string = MergeTupleConvertString(test, past_prayer_msg)
                            #new_string = remove_extra_char(resultant_string)
                            past_prayer_msg = remove_extra_char(past_prayer_msg)
                            return new_string + past_prayer_msg
                    
                    else:
                        #msg = str(Nearest_hrs_diff)+" hours "+ str(newDiff_mins)+ " minutes more until "+ str(SetPrayer)+ " time."
                        print(Nearest_hrs_diff,"hours", newDiff_mins, "minutes more until", SetPrayer, "time.") #return
                        
                        test = Nearest_hrs_diff, "hours ", newDiff_mins, " minutes more until ", SetPrayer, " time.#"
                        #test1 = SetPrayer, "passed! Hurry."
                        #original_string = str(test)
                        #print(original_string)
                        new_string = remove_extra_char(test)
                        print("MW4")
                        if(isEmpty(past_prayer_msg)):
                            
                            return new_string
                        else:
                            #resultant_string = MergeTupleConvertString(test, past_prayer_msg)
                            #new_string = remove_extra_char(resultant_string)
                            
                            """
                            string_past_prayer_msg = str(past_prayer_msg) # string version of tuple
                            output_past_prayer_msg = remove_extra_char(string_past_prayer_msg) # output/webpage display version
                            return output_past_prayer_msg + new_string
                            """
                            past_prayer_msg = remove_extra_char(past_prayer_msg)
                            return new_string + past_prayer_msg
                        #return render_template('refresh.html', msg=time.time())
                    print("After ret, before tim.sleep")
                    time.sleep(60)

                #Nearest_mins_diff == 0 OR currentMinute_int == Nearest_mins, prayer hour not same, so printing remaining hours only
                else: 
                    print(Nearest_hrs_diff, "hours more until", SetPrayer, "time.") #return
                    test = Nearest_hrs_diff, "hours more until", SetPrayer, "time.#" # "#" is for splitting joined strings and displaying on webpage
                    #original_string = str(test)
                    new_string = remove_extra_char(test)

                    print("MW5")
                    if(isEmpty(past_prayer_msg)):
                        return new_string
                    else:
                        #resultant_string = MergeTupleConvertString(test, past_prayer_msg)
                        #new_string = remove_extra_char(resultant_string)
                        past_prayer_msg = remove_extra_char(past_prayer_msg)
                        return new_string + past_prayer_msg
                    print("After ret, before tim.sleep")
                    time.sleep(60)

            # Will be used for sending msg about FAJR Salah only for the next day, i.e after isha msg of current day. Include actual time + countdown
            elif (currentHour_int > Nearest_hrs):  
                #diff_hrs = 24 + diff_hrs  #Next day salah time (Added 24 to make diff_hrs value positive)
                if(currentMinute_int < Nearest_mins):
                    print("Next prayer:", SetPrayer, "in", Nearest_hrs_diff, "hours", Nearest_mins_diff, "minutes.") #return
                    #msg = "Next prayer: " + str(SetPrayer)+ " in "+ str(Nearest_hrs_diff) +" hours " + str(Nearest_mins_diff)+ " minutes"
                    #return msg + render_template('refresh.html')
                    test = "Next prayer:", SetPrayer, "in", Nearest_hrs_diff, "hours", Nearest_mins_diff, "minutes.#"
                    #original_string = str(test)
                    new_string = remove_extra_char(test)
                    print("MW6")
                    if(isEmpty(past_prayer_msg)):
                        return new_string
                    else:
                        #resultant_string = MergeTupleConvertString(test, past_prayer_msg)
                        #new_string = remove_extra_char(resultant_string)
                        past_prayer_msg = remove_extra_char(past_prayer_msg)
                        return new_string + past_prayer_msg
                    print("After ret, before tim.sleep")
                    time.sleep(60)
                    
                elif(currentMinute_int > Nearest_mins):
                    newDiff_mins = 60 + Nearest_mins_diff #Add 60 to diff_mins to find the correct remaining minutes
                    print("Next prayer:", SetPrayer, "in", Nearest_hrs_diff, "hours", newDiff_mins, "minutes") #return
                    #msg = "Next prayer: " + str(SetPrayer)+ " in "+ str(Nearest_hrs_diff) +" hours " + str(newDiff_mins)+ " minutes"
                    #return render_template('refresh.html', msg=msg)
                    
                    test = "Next prayer:", SetPrayer, "in", Nearest_hrs_diff, "hours", newDiff_mins, "minutes#"
                    #original_string = str(test)
                    new_string = remove_extra_char(test)
                    print("MW7")
                    if(isEmpty(past_prayer_msg)):
                        return new_string
                    else:
                        #resultant_string = MergeTupleConvertString(test, past_prayer_msg)
                        #new_string = remove_extra_char(resultant_string)
                        past_prayer_msg = remove_extra_char(past_prayer_msg)
                        return new_string + past_prayer_msg
                    #return (msg)
                    print("After ret, before tim.sleep")
                    time.sleep(60)
                else: #diff_mins == 0, so printing hours only
                    print("Next prayer:", SetPrayer, "in", Nearest_hrs_diff, "hours") #return
                
                    test = "Next prayer:", SetPrayer, "in", Nearest_hrs_diff, "hours#"
                    #original_string = str(test)
                    new_string = remove_extra_char(test)
                    print("MW8")
                    if(isEmpty(past_prayer_msg)):
                        return new_string
                    else:
                        #resultant_string = MergeTupleConvertString(test, past_prayer_msg)
                        #new_string = remove_extra_char(resultant_string)
                        past_prayer_msg = remove_extra_char(past_prayer_msg)
                        return new_string + past_prayer_msg
                    time.sleep(60)
            
            # currentHour is prayerHour
            else:
                if(currentMinute_int < Nearest_mins):
                    #print("Prayer in", Nearest_mins_diff, "minutes.")
                    print("Prayer:", SetPrayer, "in", Nearest_mins_diff, "minutes.") #return
                    print("#######################################################")
                    
                    test = "Prayer:", SetPrayer, "in", Nearest_mins_diff, "minutes.#"

                    #original_string = str(test)
                    new_string = remove_extra_char(test)
                    print("MW9")
                    if(isEmpty(past_prayer_msg)):
                        return new_string
                    else:
                        #resultant_string = MergeTupleConvertString(test, past_prayer_msg)
                        #new_string = remove_extra_char(resultant_string)
                        past_prayer_msg = remove_extra_char(past_prayer_msg)
                        return new_string + past_prayer_msg
                    time.sleep(60)
                # Later feature - "Prayed the <Salah>?": When HTML YES/NO button incorporated in email message. 
                elif(currentMinute_int > Nearest_mins):
                    print(abs(Nearest_mins_diff), "minutes past", SetPrayer, "time. Lets get it done!") #return
                    
                    print(NearestUpcoming_min_diff_hrs, "hours and", NearestUpcoming_min_diff_minutes, "kminutes more until", UpcomingPrayer, "time.")
                    test = abs(Nearest_mins_diff), "minutes past", SetPrayer, "time. Lets get it done!#"
                    #original_string = str(test)
                    new_string = remove_extra_char(test)
                    print("MW10")
                    if(isEmpty(past_prayer_msg)):
                        return new_string
                    else:
                        #resultant_string = MergeTupleConvertString(test, past_prayer_msg)
                        #new_string = remove_extra_char(resultant_string)
                        past_prayer_msg = remove_extra_char(past_prayer_msg)
                        return new_string + past_prayer_msg
                    time.sleep(60)

                # Prayer hour and prayer minute (0 difference for both)    
                else:
                    print(SetPrayer, "Prayer Time!!\nUpcoming Parayer:", UpcomingPrayer, "in", NearestUpcoming_min_diff_hrs, "hours", NearestUpcoming_min_diff_minutes) #return

                    test = SetPrayer, "Prayer Time!!#Upcoming Parayer:", UpcomingPrayer, "in", NearestUpcoming_min_diff_hrs, "hours", NearestUpcoming_min_diff_minutes
                    #original_string = str(test)
                    new_string = remove_extra_char(test)
                    
                    message = SetPrayer+ " Prayer Time!!\nUpcoming Parayer: "+ UpcomingPrayer + " at "+ str(digitalTime) +":"+ Prayers[UpcomingPrayer][1] + ".\nIn " + str(NearestUpcoming_min_diff_hrs)+ " hours and " + str(NearestUpcoming_min_diff_minutes) + " minutes."
                    # if statement here - upon sign up for email reminder
                    alert(sender, password, email_title, recipient, message)
                    #count = 0 # restart counter, so new SetPrayer and UpcomingPrayer is set.
                    #minDiff = 24 # To set new SetPrayer and UpcomingPrayer. (Otherwise mindiff is 0)
                    
                    return new_string
                    time.sleep(60)
        except Exception as e:
            print(e)
            error_msg = "Your local time could not be set successfully :(#Please make sure Country and City information is accurate."
            print("Current local time could not be set successfully")
            return error_msg
            time.sleep(60)

    #endofwhile
    #print("NearestminDiff:", Nearest_mins_diff, "Nearest_hrs:", Nearest_hrs, "currentHour_int:", currentHour_int, "currentMinute_int:", currentMinute_int, "Nearest_mins: ", Nearest_mins)        
#endofFunction

@app.route("/")
def hello():
    return findNearestDifference()          
if __name__ == "__main__" :
    app.run(debug=True)




#--------------------------------------------------------END--------------------------------#         
