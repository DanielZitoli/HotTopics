def display_date(date):
    date = str(date)
    months = ["January", "Febuary", "March", "April", "May", "June", "July", "August", "Semptember", "October", "November", "December"]
    year = date[:4]
    month = months[int(date[5:7]) - 1]
    return "{0}, {1}".format(month, year)
