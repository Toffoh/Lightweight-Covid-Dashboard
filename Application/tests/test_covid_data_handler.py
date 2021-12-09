import json
import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

import covid_data_handler

with open('config.json') as cfg:
    json_values = json.load(cfg)
    sample_data = json_values['sample_data']

def test_parse_csv_data():
    data = covid_data_handler.parse_csv_data(sample_data)
    assert len(data) == 639

def test_process_covid_csv_data():
    last7days_cases , current_hospital_cases , total_deaths = covid_data_handler.process_covid_csv_data ( covid_data_handler.parse_csv_data ( sample_data ) )
    assert last7days_cases == 240299
    assert current_hospital_cases == 7019
    assert total_deaths == 141544

def test_covid_API_request():
    data = covid_data_handler.covid_API_request()
    assert isinstance(data, dict)

