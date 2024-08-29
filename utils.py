import datetime
def get_today_date():
    weekno = datetime.datetime.today().weekday()

    if weekno > 5:
        raise Exception ('Its a weekend, market is closed')
    else: 
        return str(datetime.date.today())
