from datetime import datetime, timedelta
from time import sleep
from picamzero import Camera

cam = Camera()
cam.still_size = (4056, 3040) # Sets the camera resolution

# Create a variable to store the start time
start_time = datetime.now()
# Create a variable to store the current time
# (these will be almost the same at the start)
now_time = datetime.now()
counter=1
# Run a loop for 1 minute
while (now_time < start_time + timedelta(minutes=1)):
    image = f"image_{counter}.jpg" # Image file name
    print("Counter", counter, "Hello ISS now:", now_time, "until:", start_time+ timedelta(minutes=10))
    cam.take_photo(image) # Takes a photo
    counter+=1
    sleep(14)
    # Update the current time
    now_time = datetime.now()
# Out of the loop — stopping