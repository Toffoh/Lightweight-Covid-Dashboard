import requests, sched, time, json
from datetime import datetime

with open('Application\\config.json') as cfg:
    json_values = json.load(cfg)
    api_key = json_values['api_key']
    search_terms = json_values['search_terms']

### access current news data and update the headlines held on the dashboard


def todays_date() -> str:
    ''' return today's date 
    --- returns = date in format=yyyy-mm-dd '''
    today = datetime.now().strftime('%Y-%m-%d')
    return today

def news_API_request(covid_terms=search_terms) -> dict:    
    ''' update news via the news API 
    --- args = (optional) search terms 
    --- returns = json with news articles '''
    request_url = 'https://newsapi.org/v2/everything?qInTitle='+covid_terms.replace(' ',' OR ')+'&from='+todays_date()+'&sortBy=relevancy&apiKey='+api_key    
    global response
    response = requests.get(request_url).json()
    return response

def update_news(update_news_interval: int) -> dict:
    ''' schedule when to update news articles 
    --- args = when to update in seconds 
    --- returns = json with news articles '''
    update_call_news = sched.scheduler(time.time, time.sleep)
    update_call_news.enter(update_news_interval,1,news_API_request)
    update_call_news.run(blocking=False)
    return response
    
