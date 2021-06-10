
from datetime import date, timedelta

# https://stackoverflow.com/a/1060330/2243490
def date_time_range(startDate, endDate):
    
    # create new date object to ignore the time
    startDate = date(startDate.year, startDate.month, startDate.day)
    endDate = date(endDate.year, endDate.month, endDate.day)
    nday = (endDate-startDate).days
    
    nday += 1 # include the first day

    for n in range(nday):
        yield startDate + timedelta(n)
