import datetime
def check_cc_expiry(expiry):
    month, year = str(expiry).split("/")
    if int(month) > 12 or int(month) < 1:
        return False
    if int(year) + 2000 < datetime.datetime.now().year:
        return False
    if int(year) + 2000 == datetime.datetime.now().year and int(month) < datetime.datetime.now().month:
        return False
    else:
        return True
