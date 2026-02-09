# Import datetime and timedelta to work with dates and time differences
from datetime import datetime, timedelta  

# Import sleep to pause execution for a given number of seconds
from time import sleep  

# Import Image to read EXIF metadata from images
from exif import Image  

# Import OpenCV for image processing
import cv2  

# Import math module for mathematical operations
import math  

# Import the Camera class to control the Pi camera
from picamzero import Camera


# Function to extract the original timestamp from an image EXIF metadata
def get_time(image):
    # Open the image file in binary read mode
    with open(image, 'rb') as image_file:
        # Load the image EXIF data
        img = Image(image_file)
        # Get the original datetime string from EXIF metadata
        time_str = img.get("datetime_original")
        # Convert the string into a datetime object
        time = datetime.strptime(time_str, '%Y:%m:%d %H:%M:%S')
    # Return the datetime object
    return time
    
    
# Function to calculate the time difference between two images
def get_time_difference(image_1, image_2):
    # Get the timestamp of the first image
    time_1 = get_time(image_1)
    # Get the timestamp of the second image
    time_2 = get_time(image_2)
    # Calculate the difference between the two timestamps
    time_difference = time_2 - time_1
    # Return the difference in seconds
    return time_difference.seconds


# Function to load two images as OpenCV grayscale images
def convert_to_cv(image_1, image_2):
    # Read the first image in grayscale mode
    image_1_cv = cv2.imread(image_1, 0)
    # Read the second image in grayscale mode
    image_2_cv = cv2.imread(image_2, 0)
    # Return both OpenCV image objects
    return image_1_cv, image_2_cv


# Function to detect ORB features and descriptors in two images
def calculate_features(image_1, image_2, feature_number):
    # Create an ORB detector with a given number of features
    orb = cv2.ORB_create(nfeatures=feature_number)
    # Detect keypoints and compute descriptors for the first image
    keypoints_1, descriptors_1 = orb.detectAndCompute(image_1_cv, None)
    # Detect keypoints and compute descriptors for the second image
    keypoints_2, descriptors_2 = orb.detectAndCompute(image_2_cv, None)
    # Return keypoints and descriptors for both images
    return keypoints_1, keypoints_2, descriptors_1, descriptors_2


# Function to match descriptors between two images
def calculate_matches(descriptors_1, descriptors_2):
    # Create a brute-force matcher using Hamming distance
    brute_force = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    # Match descriptors from both images
    matches = brute_force.match(descriptors_1, descriptors_2)
    # Sort matches by distance (best matches first)
    matches = sorted(matches, key=lambda x: x.distance)
    # Return the sorted list of matches
    return matches
    
    
# Function to extract matching coordinates from keypoints
def find_matching_coordinates(keypoints_1, keypoints2, matches):
    # List to store coordinates from the first image
    coordinates_1 = []
    # List to store coordinates from the second image
    coordinates_2 = []
    # Loop through all matches
    for match in matches:
        # Index of the keypoint in the first image
        image_1_idx = match.queryIdx
        # Index of the keypoint in the second image
        image_2_idx = match.trainIdx
        # Get (x, y) coordinates from the first image
        (x1, y1) = keypoints_1[image_1_idx].pt
        # Get (x, y) coordinates from the second image
        (x2, y2) = keypoints_2[image_2_idx].pt
        # Append coordinates to the lists
        coordinates_1.append((x1, y1))
        coordinates_2.append((x2, y2))
    # Return the matching coordinates from both images
    return coordinates_1, coordinates_2


# Function to calculate the average distance between matching points
def calculate_mean_distance(coordinates_1, coordinates_2):
    # Variable to accumulate all distances
    all_distances = 0
    # Pair corresponding coordinates from both images
    merged_coordinates = list(zip(coordinates_1, coordinates_2))
    # Loop through each pair of coordinates
    for coordinate in merged_coordinates:
        # Calculate difference in x direction
        x_difference = coordinate[0][0] - coordinate[1][0]
        # Calculate difference in y direction
        y_difference = coordinate[0][1] - coordinate[1][1]
        # Calculate Euclidean distance
        distance = math.hypot(x_difference, y_difference)
        # Add distance to the total
        all_distances = all_distances + distance
    # Return the mean distance
    return all_distances / len(merged_coordinates)


# Function to calculate speed in kilometers per second
def calculate_speed_in_kmps(feature_distance, GSD, time_difference):
    # Convert pixel distance to kilometers using GSD
    distance = feature_distance * GSD / 100000
    # Calculate speed as distance over time
    speed = distance / time_difference
    # Return the calculated speed
    return speed


# Store the starting time of the program
start_time = datetime.now()

# Initialize the camera
cam = Camera()

# Set camera resolution
cam.still_size = (4056, 3040)

# Store the current time
now_time = datetime.now()

# Initialize image counter
counter = 1

# Run the loop for 1 minute
while (now_time < start_time + timedelta(minutes=1)):
    # Generate image filename
    image = f"image_{counter}.jpg"
    
    # Print status information
    print("Counter", counter, "Hello ISS now:", now_time, "until:", start_time + timedelta(minutes=1))
    
    # Capture a photo
    cam.take_photo(image)
    
    # Wait 2 seconds before next capture
    sleep(2)
    
    # Process images only if at least two images exist
    if counter > 1:
        # Calculate time difference between consecutive images
        time_difference = get_time_difference(
            f"image_{counter-1}.jpg",
            f"image_{counter}.jpg"
        )
        
        # Convert images to OpenCV format
        image_1_cv, image_2_cv = convert_to_cv(
            f"image_{counter-1}.jpg",
            f"image_{counter}.jpg"
        )
        
        # Detect keypoints and descriptors
        keypoints_1, keypoints_2, descriptors_1, descriptors_2 = calculate_features(
            image_1_cv, image_2_cv, 1000
        )
        
        # Match descriptors between images
        matches = calculate_matches(descriptors_1, descriptors_2)
        
        # Extract matching coordinates
        coordinates_1, coordinates_2 = find_matching_coordinates(
            keypoints_1, keypoints_2, matches
        )
        
        # Calculate average feature displacement
        average_feature_distance = calculate_mean_distance(coordinates_1, coordinates_2)
        
        # Calculate speed
        speed = calculate_speed_in_kmps(
            average_feature_distance, 12648, time_difference
        )
        
        # Create a list to store speed values
        speed_list = []
        speed_list.append(speed)
        
        # Print the speed list
        print(speed_list)
    
    # Increment image counter
    counter += 1
    
    # Update current time
    now_time = datetime.now()


# Calculate average speed after the loop
length = len(speed_list)
amount = sum(speed_list)
average = amount / length

# Format the average speed
string = str(f"{average:.4f}")

# Print the average speed
print(average)

# Write the result to a text file
with open("result.txt", "w", encoding="utf-8") as result:
    result.write(string)
        
# End of the program
