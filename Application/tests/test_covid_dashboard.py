from .. import covid_dashboard
### test to see if update_data adds items to the queue
def test_update_data():
    a,b,c,d = covid_dashboard.update_data(5)
    assert d != []

def test_update_data_cancel():
    a,b,c,d = covid_dashboard.update_data(5,'yes')
    assert d == []

def test_updates_column():
    output = covid_dashboard.updates_column('data',5,'test update',3)
    assert isinstance(output,list)

