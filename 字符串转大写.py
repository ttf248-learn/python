import datetime

init_time = datetime.datetime.strptime("08:50", "%H:%M")
close_price = datetime.datetime.strptime("13:58", "%H:%M")

init_time_cron = f"{init_time.minute} {init_time.hour} * * 1-5"
close_price_cron = f"{close_price.minute} {close_price.hour} * * 1-5"

print("Init Time Cron:", init_time_cron)
print("Close Price Cron:", close_price_cron)
