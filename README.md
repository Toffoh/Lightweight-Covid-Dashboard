
**Covid Dashboard**
===============

introduction
---------------

The purpose of the project is to gather and process data of the Sars-cov-2 virus and the coronavirus/covid-19 disease.

The end goal is to have reliable data taken from the governments Covid-19 API and the news API in a readable UI with up to date data.

Prerequisites
---------------	

Internet connection to access multiple APIs

Developed on python 3.8.3

Installation
---------------	

**Dependencies**

1. Flask
2. Requests
3. pytest
4. sched


Getting started tutorial
---------------	

Ensure all dependencies are installed
The main app is 'Covid_dashboard' and calls other modules on requirement
nation_2021_10_28.csv is included for testing purposes 

Testing
---------------	

Tests can be run from the /<tests>/ directory
They will automatically run to ensure the program is running correctly

Developer Documentation
---------------	

**covid_data_handler**

Function(parse_csv_data: str) -> list:
 '''This takes argument=string as a csv filename and reads the data and writes it to a list object'''

Function(process_csv_data: list) -> dict:
 '''This takes the list object returned by Function(parse_csv_data) and returns those statistics'''

Function(covid_API_request: str) -> dict:
 '''This updates the csv using the COVID-19 API '''
_API documentation: https://coronavirus.data.gov.uk/details/developers-guide_

Function(schedule_covid_updates)
 '''schedules the covid_API_request function to run at a given interval'''

**covid_news_handling**

Function(todays_date: int) -> str:
 '''returns today's date as a string with format YYYY-MM-DD'''

Function(news_API_request: str) -> dict:
 '''This updates the news articles using the news api'''
_API documentation: https://newsapi.org/docs_

Function(update_news)
 '''This schedules the news_API_request function'''

**covid_dashboard**

Function(Index)
 '''This tells the program to render the dashboard from the index.html template'''

Function(data_assign)
 '''This assigns data to output variables using parse_csv_data and process_csv_data'''

Function(update_news: int) -> dict
 '''This calls for news to be updated on schedule'''

Function(update_data) 
 '''This calls for data to be updated on shcedule'''

Function(update_articles: int) -> list:
 '''This updates the news articles and adds them to the dashboard'''

Function(time_to_sec: str) -> int:
 '''Converts HH:MM:SS to seconds'''

Function(sec_to_time:int ) -> str:
 '''Converts seconds to HH:MM:SS'''

Function(time_difference: int) -> str:
 '''Takes time difference in seconds and returns time difference in HH:MM:SS'''

Function(start_time)
 '''When the program makes a request this makes a timestamp'''

Function(log_requests)
 '''Tells the logger to log the specified data when a response is given'''

Details
---------------	

Author: Ryan Toffoletti

