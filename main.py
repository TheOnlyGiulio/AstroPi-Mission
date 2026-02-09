from datetime import datetime, timedelta
from time import sleep
from exif import Image
import cv2
import math
from picamzero import Camera

def get_time(image):
    with open(image, 'rb') as image_file:
        img = Image(image_file)
        time_str = img.get("datetime_original")
        time = datetime.strptime(time_str, '%Y:%m:%d %H:%M:%S')
    return time
    
    
def get_time_difference(image_1, image_2):
    time_1 = get_time(image_1)
    time_2 = get_time(image_2)
    time_difference = time_2 - time_1
    return time_difference.seconds


def convert_to_cv(image_1, image_2):
    image_1_cv = cv2.imread(image_1, 0)
    image_2_cv = cv2.imread(image_2, 0)
    return image_1_cv, image_2_cv


def calculate_features(image_1, image_2, feature_number):
    orb = cv2.ORB_create(nfeatures = feature_number)
    keypoints_1, descriptors_1 = orb.detectAndCompute(image_1_cv, None)
    keypoints_2, descriptors_2 = orb.detectAndCompute(image_2_cv, None)
    return keypoints_1, keypoints_2, descriptors_1, descriptors_2


def calculate_matches(descriptors_1, descriptors_2):
    brute_force = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = brute_force.match(descriptors_1, descriptors_2)
    matches = sorted(matches, key=lambda x: x.distance)
    return matches
    
    
def find_matching_coordinates(keypoints_1, keypoints2, matches):
    coordinates_1 = []
    coordinates_2 = []
    for match in matches:
        image_1_idx = match.queryIdx
        image_2_idx = match.trainIdx
        (x1,y1) = keypoints_1[image_1_idx].pt
        (x2,y2) = keypoints_2[image_2_idx].pt
        coordinates_1.append((x1,y1))
        coordinates_2.append((x2,y2))
    return coordinates_1, coordinates_2


def calculate_mean_distance(coordinates_1, coordinates_2):
    all_distances = 0
    merged_coordinates = list(zip(coordinates_1, coordinates_2))
    for coordinate in merged_coordinates:
        x_difference = coordinate[0][0] - coordinate[1][0]
        y_difference = coordinate[0][1] - coordinate[1][1]
        distance = math.hypot(x_difference, y_difference)
        all_distances = all_distances + distance
    return all_distances / len(merged_coordinates)


def calculate_speed_in_kmps(feature_distance, GSD, time_difference):
    distance = feature_distance * GSD / 100000
    speed = distance / time_difference
    return speed

# Create a variable to store the start time
start_time = datetime.now()
cam = Camera()
cam.still_size = (4056, 3040)
# Create a variable to store the current time
# (these will be almost the same at the start)
now_time = datetime.now()
counter=1
# Run a loop for 1 minute
while (now_time < start_time + timedelta(minutes=1)):
    image = f"image_{counter}.jpg" # Image file name
    print("Counter", counter, "Hello ISS now:", now_time, "until:", start_time+ timedelta(minutes=1))
    cam.take_photo(image) # Takes a photo
    sleep(5)
    # Update the current time
    if counter>1:
        time_difference = get_time_difference(f"image_{counter-1}.jpg", f"image_{counter}.jpg") #get time difference between images
        image_1_cv, image_2_cv = convert_to_cv(f"image_{counter-1}.jpg", f"image_{counter}.jpg") #create opencfv images objects
        keypoints_1, keypoints_2, descriptors_1, descriptors_2 = calculate_features(image_1_cv, image_2_cv, 1000) #get keypoints and descriptors
        matches = calculate_matches(descriptors_1, descriptors_2) #match descriptors
        coordinates_1, coordinates_2 = find_matching_coordinates(keypoints_1, keypoints_2, matches)
        average_feature_distance = calculate_mean_distance(coordinates_1, coordinates_2)
        speed = calculate_speed_in_kmps(average_feature_distance, 12648, time_difference)
        speed_list= []
        speed.append(speed_list)
        print(speed_list)
        length = len(speed_list)
        amount = sum(speed_list)
        average = amount/length
        string = str(average)
        print(average)
        with open("result.txt","w",encoding="utf-8") as result:
            result.write(string)
    counter+=1
    now_time = datetime.now()
        
# Out of the loop — stopping