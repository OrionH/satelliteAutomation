"""
=====================================================================
Name:           Orion Humphrey
Class:          INOV2010
Assignment:     N/A
Due Date:       Mon May 1, 2020 at 11:59pm
Version:        1
Description:    This is a test of n2yo API
Notes:          ohumphre@uccs.edu
TODO:           Set up TLE time decoding for offline use
                Set up timestamps on files
                Configure with rtl_sdr for raw I/Q recording
                Pylint
                Propper README
=====================================================================
"""
import requests
import json
import os
import datetime
#import subprocess
def main():
    #inputs
    #PUT YOUR API KEY HERE
    apiKey = ''

    #https://www.n2yo.com/database/
    noradID = input('Enter NORAD ID of satelite to track(NOAA-15=25338, NOAA-18=28654): ') or '25338'
    latitude = input('Observer latitude (Default=COS): ') or '38.83'
    lognitude = input('Observer longitude (Default=COS): ') or '-104.82'
    altitude = input('Observer altitude (Default=COS): ') or '1839'
    daysPresented = input('Enter days to track (Default=1): ') or '1'
    #Elevation recommended to be 13+ degrees for visible passes
    elevation = input('Enter minimum elevation to check for in degrees (Default=13): ') or '13'

    print('\nWaiting for API...\n')


    # #API Test block
    # response = requests.get(f' https://api.n2yo.com/rest/v1/satellite/&apiKey={apiKey}')
    # if response:
    #     print("API connection succesful")
    # else:
    #     print (f"API error: {response}")


    #Getting radio passes data from API. Pass data gets returned as json.
    getRadioPasses =  requests.get(f'https://api.n2yo.com/rest/v1/satellite/radiopasses/{noradID}/{latitude}/{lognitude}/{altitude}/{daysPresented}/{elevation}/&apiKey={apiKey}')
    passData = json.loads(getRadioPasses.text)

    # #Getting current user (Only needs to be used when running script with sudo which is not required)
    # #Edit the at command with su 'user' or su {loggedIn}
    # process = subprocess.Popen(['whoami'], stdout=subprocess.PIPE)
    # stdout = process.communicate()[0]
    # loggedIn = (stdout.decode('utf-8'))
    # print(loggedIn)


    #items = [data['passes'][i]['startUTC'] for i in range(data['info']['passescount'])]

    #Parsing start times from radio pass data and saving to a list
    startTimes =[]
    for i in range(passData['info']['passescount']):
        startTimes.append(passData['passes'][i]['startUTC'])
    #print(startTimes)

    #Parsing end times from radio pass data and saving to a list
    endTimes =[]
    for i in range(passData['info']['passescount']):
        endTimes.append(passData['passes'][i]['endUTC'])
    #print(endTimes)

    #Calculating total pass time from parsed start and end times
    totalTime = []
    for i in range(passData['info']['passescount']):
        totalTime.append(endTimes[i]-startTimes[i])
    #print(totalTime)

    #For every pass in the days selected, schedule rtl_fm to record a local fm station's audio at the parsed times.
    for i in range(passData['info']['passescount']):
        #Convert unix time into readable time to pass into the at command.
        readableDate = str(datetime.datetime.utcfromtimestamp(startTimes[i]).date())
        readableTime = datetime.datetime.utcfromtimestamp(startTimes[i]).time()
        #print(f'Scheduling task at: {readableDate}, {readableTime.hour:02d}:{readableTime.minute:02d}')

        #Open and save an rtl_fm command with a timeout that will be read into an "at" command to schedule the job
        #Command must be saved into a file and not piped since pipes run concurently
        #Every pass will be saved as a new file with a different length of time
        #Time must contain two digits to not break the "at command"
        #Make sure to claim ownership of the file in linux so the program can write to it
        with open('commandFile', 'w') as file:
            #http://kmkeen.com/rtl-demod-guide/2013-01-02-17-54-37-499.html
            file.write(f'timeout {totalTime[i]} rtl_fm -M wbfm -f 96.9M | sox -r 32k -t raw -e s -b 16 -c 1 -V1 - fm{i}.wav')

        os.system(f'at -f commandFile {readableTime.hour:02d}:{readableTime.minute:02d} {readableDate}')



# Calling main
if __name__ == "__main__":
    main()
