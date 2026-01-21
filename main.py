from datetime import datetime, timedelta
from time import sleep


# Rullino, molto carino, pino

# Create a variable to store the start time
start_time = datetime.now()
# Create a variable to store the current time
# (these will be almost the same at the start)
now_time = datetime.now()
counter=1
# Run a loop for 1 minute
while (now_time < start_time + timedelta(minutes=1)):
    print("Counter", counter, "Hello ISS now:", now_time, "until:", start_time+ timedelta(minutes=1))
    counter+=1
    sleep(10)
    # Update the current time
    now_time = datetime.now()
# Out of the loop — stopping