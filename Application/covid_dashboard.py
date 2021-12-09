### Imports ###
from flask import Flask, render_template, g
from flask import request as req
import sched, time, json, pytest, logging
from covid_data_handler import parse_csv_data, process_covid_csv_data, covid_API_request, schedule_covid_updates
from covid_news_handling import news_API_request, update_news,todays_date
from datetime import datetime

''' Create a custom logger so we can control what is being logged'''
logr = logging.getLogger('__name__')
logr.setLevel(logging.INFO)
log_handler = logging.FileHandler('Logs/sys.log')
log_handler.setLevel(logging.INFO)
log_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
log_handler.setFormatter(log_formatter)
logr.addHandler(log_handler)

### Global variables ###
news = []
update = []
update_scheduled_times = []
removed_articles = []
app = Flask(__name__)
s = sched.scheduler(time.time, time.sleep)
national_data_csv = ''
local_data_csv = ''
template = ''
image_file_path = ''
with open('config.json') as cfg:
    json_values = json.load(cfg)
    national_data_csv = json_values['nation_data']
    local_data_csv = json_values['local_data']
    template = json_values['template_name']
    image_file_path = json_values['title_image']
    log_dir=json_values['log_dir']

def run_tests():
    ''' run tests in tests folder, by default, tests are run every 3 minutes after a refresh
    hence aggregating to one per minute as the app runs for enough time'''
    retcode = pytest.main()

def data_assign(): 
    ''' assign value to the variables that will form the data for the dashboard '''
    global national_7_day_cases 
    global national_hosp_cases 
    global national_deaths_total 
    global local_7_day_cases 
    national_7_day_cases, national_hosp_cases, national_deaths_total = process_covid_csv_data(parse_csv_data(national_data_csv))
    local_7_day_cases,a,b = process_covid_csv_data(parse_csv_data(local_data_csv))
    
data_assign()

def update_articles(update_interval: int) -> list: 
    ''' update news articles list and then add them to the dashboard, as long as they are not excluded --- args = time in seconds till news should update'''
    news_data = update_news(update_interval)
    news.clear()
    
    for article in news_data['articles']:
        if article['title'] not in removed_articles:
            news.append(article)
#call for the articles to be collated on run  
update_articles(0)      

def update_data(interval: int,cancel='no'):
    ''' update the data for the covid stats that will appear on the dashboard, unless the update is cancelled 
    --- args = time in seconds till data should update, if the update should be cancelled 
    --- returns = events to update the data, the queue of updates'''
    event1 = s.enter(interval,1,schedule_covid_updates,argument=(0,'national','England','Nation'))
    event2 = s.enter(interval,2,schedule_covid_updates,argument=(0,'local'))#interval for schedule_covid_updates is 0 as the interval is already defined in s
    event3 = s.enter(interval,3,data_assign)
    
    if cancel != 'no':
        list(map(s.cancel, s.queue))
    q = s.queue
    return event1, event2, event3, q

def time_to_sec(time_str: str) -> int:
    ''' convert from HH:SS:MM to seconds
    --- args = time in format HH:MM:SS
    --- returns = time in seconds'''
    h, m, s = time_str.split(':')
    return int(h)*3600+int(m)*60+int(s)

def sec_to_time(time_in_sec: int) -> str:
    ''' convert from seconds to HH:SS:MM 
    --- args = time in seconds
    --- returns = time in format HH:MM:SS'''
    hours = time_in_sec // (60*60)
    time_in_sec %= (60*60)
    minutes = time_in_sec // 60
    time_in_sec %= 60
    return "%02i:%02i:%02i" % (hours, minutes, time_in_sec)


def time_difference(time_1: int) -> str:
    ''' takes a time delta in seconds and returns it in HHMMSS 
    args = difference between two times in seconds
    returns = difference between two times in HH:MM:SS'''
    t2 = time.time()+time_1
    time_diff_in_hhmmss = datetime.fromtimestamp(t2).strftime('%H:%M')
    return time_diff_in_hhmmss


def updates_column(update_type: str, time_of_update: str, update_title: str, time_to_update: int) -> list:
    ''' when an update is scheduled, add it to the list of upcoming updates, and log the time it will update to be removed when it has occurred 
    args = news or data, when the update will happen, the title of the update, time between now and when it updates in seconds
    returns = list of upcoming updates'''
    upcoming_updates = {'title':update_title,
                        'content':update_type+' will be updated at '+str(time_of_update),}
    update.append(upcoming_updates)
    update_scheduled_times.append(time_to_update+time.time())
    return update

@app.before_request
def start_time():
    ''' start a timer before requests are made '''
    g.start = time.time()

@app.route('/index')

def index():
    ''' the main server function '''
    
    s.enter(180,1,run_tests)
    s.run(blocking=False)
    text_field = req.args.get('two')
    update_time = req.args.get('update')
    time_to_update = 0
    
    if update_time: # hh:mm
        t1 = time_to_sec(update_time+':00') # doesn't have seconds, can arbitrarily add 00s to the end
        t2 = time_to_sec(str(time.strftime('%H:%M:%S')))
        time_to_update = t1-t2 # to be used to schedule updates
        if time_to_update < 0:
            time_to_update = 86400+time_to_update
    should_update_news = req.args.get('news')
    should_update_data = req.args.get('covid-data')
    should_remove_update = req.args.get('update_item')
    should_repeat_update = req.args.get('repeat')

    if text_field: # if there is anything entered in the text field, then users requests have been submitted
        if should_update_news: # if news update is requested, queue it, then add it to the update column  
            if time_to_update != 0:
                update_articles(time_to_update)
                updates_column('News',time_difference(time_to_update),text_field+' (news)',time_to_update)

        if should_update_data: # if data update is requested, queue it, then add it to the update column 
            if time_to_update != 0:
                update_data(time_to_update)
                updates_column('Data',time_difference(time_to_update),text_field+ ' (data)',time_to_update)

    if should_remove_update: # check if a scheduled update is cancelled
        for item in update:
            if item['title']==should_remove_update:
                update.remove(item)
                update_data(time_to_update,'yes')

    if should_repeat_update: # check if update should be repeated, then check what to update, then add to updates column
        if should_update_news:
            update_articles(time_to_update*2)
            updates_column('News',time_difference(time_to_update*2),text_field+' (news)'+ ' repeat',time_to_update*2)
        if should_update_data:
            update_data(time_to_update*2)
            updates_column('Data',time_difference(time_to_update*2),text_field+' (data)'+' repeat',time_to_update*2)
    ### below is a very convoluted workaround to a bug i experienced when multiple updates had to be removed after they had occurred
    ### due to "pop"ing the item from the list in ascending order, the index's after that event changed, so some completed updates were staying till the next refresh
    ### To overcome this, I made a new list and reversed it, so the list items would be "pop"ed from right to left
    dead_updates = []
    for u in update_scheduled_times:
        if u-time.time() <= 0:
            try:
                ind = update_scheduled_times.index(u)
                dead_updates.insert(ind,u)
            except IndexError:
                continue
    dead_updates.reverse()
    for x in dead_updates:
        if x-time.time() <= 0:
            try:
                indx = update_scheduled_times.index(x)
                update.pop(indx)
                update_scheduled_times.pop(indx)
            except IndexError:
                continue
    excluded_articles = req.args.get('notif') # check if any articles have been removed by user, and if so store them so we can exclude them from future updates
    if excluded_articles:
        excluded_list = [excluded_articles]
        removed_articles.extend(excluded_list)
        
    for item in news: # removes articles from news headlines display
        if item['title'] in removed_articles:
            news.remove(item)        
    
    # This renders our dashboard, all variables are calculated then assigned to index.html template in the 'templates' folder
    return render_template(template,title='Daily update - {}'.format(todays_date()),
                           news_articles=news,
                           deaths_total=('Total deaths in UK : '+str(national_deaths_total)),
                           nation_location='England',
                           location='Exeter',
                           national_7day_infections=national_7_day_cases,
                           hospital_cases=('National hospital cases : '+str(national_hosp_cases)),
                           local_7day_infections=local_7_day_cases,
                           updates=update,
                           image=image_file_path)

@app.after_request
def log_requests(response):
    ''' add info about the requests to the log file using our custom logger '''

    if req.path.startswith('/static'):
        return response
    now = time.time()
    duration = round(now - g.start,2)
    timestamp = datetime.now().strftime('%Y-%m-%d | %H:%M:%S')
    host = req.host.split(':',1)[0]
    args = dict(req.args)
    request_id = req.headers.get('X-Request-ID')
    log_structure = {
            "method": req.method,
            "path": req.path,
            "status": response.status_code,
            "duration": duration,
            "host": host,
            "params": args,
        }
    logr.info(str(log_structure))
    return response

#start the program
if __name__=='__main__':
    app.run()