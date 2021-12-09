from .. import covid_news_handling
def test_news_API_request():
    assert covid_news_handling.news_API_request()
    assert covid_news_handling.news_API_request('Covid COVID-19 coronavirus') == covid_news_handling.news_API_request()

def test_update_news():
    covid_news_handling.update_news(5)

