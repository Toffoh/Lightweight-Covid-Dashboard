### Imports
import csv, json, requests, sched, time
from datetime import datetime

config_dir = "Application\\config.json"

with open(config_dir) as cfg:
    jsonValues = json.load(cfg)
    current_covid_data_structure = jsonValues['current_covid_data_structure']
##open, read and copy the data from the sample csv to a list object

def parse_csv_data(csv_filename: str) -> list:
    ''' read through a csv and return a list where each entry is a row of the csv 
    --- args = string filename of csv
    --- returns = list of rows of csv'''
    
    with open(csv_filename) as csv_data:
        csv_parser = csv.reader(csv_data)
        csv_output_list = [] #create the list we want to add the rows to
        for row in csv_parser:
            csv_output_list.append(row)  #this adds each row to the list as it's own string
            
        return csv_output_list

###Process the data such that we can return cases over 7 days, current hospital cases, and total deaths per specimen date


def process_covid_csv_data(covid_csv_data: list) -> dict: 
    ''' use the data within the list filled by parse_csv_data
    --- args = list of data to process
    --- returns = cases over 7 days, current hosp cases, total deaths'''
    title_list = covid_csv_data[0]
    master_dictionary = {}
    
    for n in range(0,len(covid_csv_data)):
        if n == 0:
            continue
        row = covid_csv_data[n]
        covid_data_dictionary = {}
        for i in range(0,len(covid_csv_data[n])):
            covid_data_dictionary[title_list[i]] = row[i]
            master_dictionary[n] = covid_data_dictionary
    
    #cases over past 7 days excluding "today" as incomplete
    #past 7 days will be the most recent in the list
    cases_past_7_days = 0
    for k in range(3,10):
        #range from 3-10 as 1 is the headers, 2 is today and entry 3 is 27/10/21 which is incomplete
        new_cases = int(master_dictionary[k]['newCasesBySpecimenDate'])
        cases_past_7_days += new_cases
    current_hosp_cases = 0
    if (master_dictionary[1]['hospitalCases']) != '':
        current_hosp_cases = int(master_dictionary[1]['hospitalCases'])
    #current hospital cases is a simple lookup

    total_deaths = 0 #set to 0 to find first non-0 value 
    for x in range(1,len(covid_csv_data)):
        if master_dictionary[x]['cumDailyNsoDeathsByDeathDate'] == '':
            continue
        daily_deaths = master_dictionary[x]['cumDailyNsoDeathsByDeathDate']
        total_deaths += int(daily_deaths)
        if total_deaths != 0:#deaths are cumulative so the first non-0 value is the total
            break
    

    return cases_past_7_days,current_hosp_cases,total_deaths

def covid_API_request(location='exeter',location_type='ltla'):
    ''' request data from the covid-19 API in the form of a json
    --- args = location, location_type
    --- returns = json of covid data for location'''
    api_url = 'https://api.coronavirus.data.gov.uk/v1/data?filters=areaName='+location+';areaType='+location_type+'&structure='+str(current_covid_data_structure).replace('\'','"')
    
    #this pieces together our url for the request; had to replace ' with " as ' was being entered as %27 on chromium browser
    returned_data = requests.get(api_url).json()
    #now we have the new data in the form of a json
    header = ['date','areaName','areaCode','newCasesBySpecimenDate','cumCasesBySpecimenDate','newCasesByPublishDate','cumDailyNsoDeathsByDeathDate','hospitalCases']
    #will use this to write the first row of the new csv
    with open('Application\\csv_data\\updated_covid_csv_data_{}.csv'.format(location),'w',encoding='UTF8',newline="") as updated_csv:
        scribe = csv.DictWriter(updated_csv,fieldnames=header)
        scribe.writeheader()
        scribe.writerows(returned_data['data'])
        #this reads through the data and puts these new data into the rows below their header
        return returned_data
   


def schedule_covid_updates(update_interval,update_name,location='exeter',location_type='ltla'):#added default arg's for location and location_type so we can use this function for up to date national data
    ''' schedule a call for the data to be updated in <update_interval> seconds via running covid_API_request,
   <location> and <location_type> are default args included to allow this to be used for multiple locations '''
    update_call = sched.scheduler(time.time, time.sleep)    
    update_call.enter(update_interval,1,covid_API_request,argument=(location,location_type))
    update_call.run(blocking=False)
