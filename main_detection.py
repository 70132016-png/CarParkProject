import cv2
import pickle
import cvzone
import numpy as np
import sqlite3
from datetime import datetime
import time

# Import database functions
from database import get_db, update_spot_status, get_spot_by_label, get_all_spots

cap = cv2.VideoCapture('carPark.mp4')
width, height = 103, 43

# Load parking positions
with open('CarParkPos', 'rb') as f:
    posList = pickle.load(f)

# Create mapping between position index and spot label
spot_mapping = {}

def initialize_spot_mapping():
    """Create mapping between array position and spot labels"""
    global spot_mapping
    spots = get_all_spots()
    
    # Sort spots by label
    spots.sort(key=lambda s: s['spot_label'])
    
    # Create mapping
    for i, spot in enumerate(spots):
        if i < len(posList):
            spot_mapping[i] = spot['spot_label']

def empty(a):
    pass

cv2.namedWindow("Vals")
cv2.resizeWindow("Vals", 640, 240)
cv2.createTrackbar("Val1", "Vals", 25, 50, empty)
cv2.createTrackbar("Val2", "Vals", 16, 50, empty)
cv2.createTrackbar("Val3", "Vals", 5, 50, empty)

def checkSpaces():
    """Check parking spaces and update database"""
    spaces = 0
    
    for i, pos in enumerate(posList):
        x, y = pos
        w, h = width, height

        imgCrop = imgThres[y:y + h, x:x + w]
        count = cv2.countNonZero(imgCrop)

        # Get spot label from mapping
        spot_label = spot_mapping.get(i, f"SPOT{i}")
        
        # Get current spot status from database
        spot = get_spot_by_label(spot_label)
        
        if spot:
            # Don't override reserved spots
            if spot['status'] == 'reserved':
                color = (0, 165, 255)  # Orange for reserved
                thic = 5
            elif count < 900:
                color = (0, 200, 0)  # Green for available
                thic = 5
                spaces += 1
                # Update database only if status changed
                if spot['status'] != 'available':
                    update_spot_status(spot_label, 'available')
            else:
                color = (0, 0, 200)  # Red for occupied
                thic = 2
                # Update database only if status changed
                if spot['status'] != 'occupied':
                    update_spot_status(spot_label, 'occupied')

            cv2.rectangle(img, (x, y), (x + w, y + h), color, thic)
            
            # Show spot label instead of count
            cv2.putText(img, spot_label, (x + 5, y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (255, 255, 255), 2)

    cvzone.putTextRect(img, f'Free: {spaces}/{len(posList)}', (50, 60), thickness=3, offset=20,
                       colorR=(0, 200, 0))

# Initialize spot mapping
try:
    initialize_spot_mapping()
    print(f"Initialized {len(spot_mapping)} parking spots")
except Exception as e:
    print(f"Error initializing spot mapping: {e}")
    print("Make sure to run app.py first to initialize the database!")

print("Starting parking detection...")
print("Press 'q' or ESC to quit")

while True:
    # Get image frame
    success, img = cap.read()
    if not success:
        break
        
    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)

    val1 = cv2.getTrackbarPos("Val1", "Vals")
    val2 = cv2.getTrackbarPos("Val2", "Vals")
    val3 = cv2.getTrackbarPos("Val3", "Vals")
    if val1 % 2 == 0: val1 += 1
    if val3 % 2 == 0: val3 += 1
    imgThres = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY_INV, val1, val2)
    imgThres = cv2.medianBlur(imgThres, val3)
    kernel = np.ones((3, 3), np.uint8)
    imgThres = cv2.dilate(imgThres, kernel, iterations=1)

    checkSpaces()
    
    # Display Output
    cv2.imshow("PARKEASE - Admin View", img)
    
    key = cv2.waitKey(10)
    if key == ord('q') or key == 27:  # 'q' or ESC to quit
        break

cap.release()
cv2.destroyAllWindows()
