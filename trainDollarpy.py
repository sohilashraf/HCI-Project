import cv2
import mediapipe as mp
from dollarpy import Recognizer, Template, Point
import numpy as np
import pickle
import os

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Function to get points from a video
def getPoints(videoURL):
    cap = cv2.VideoCapture(videoURL)
    points = []

    with mp_hands.Hands(min_detection_confidence=0.9, min_tracking_confidence=0.8) as hands:
        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(image)

                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        for landmark in hand_landmarks.landmark:
                            x, y = landmark.x, landmark.y
                            if not (np.isnan(x) or np.isnan(y)):
                                points.append(Point(x, y, stroke_id=0))
            else:
                break

    cap.release()
    return points if points else []

# Function to get points from an image
def getPointsFromImage(image_path):
    points = []
    image = cv2.imread(image_path)

    with mp_hands.Hands(min_detection_confidence=0.9, min_tracking_confidence=0.8) as hands:
        if image is not None:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = hands.process(image_rgb)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    for landmark in hand_landmarks.landmark:
                        x, y = landmark.x, landmark.y
                        if not (np.isnan(x) or np.isnan(y)):
                            points.append(Point(x, y, stroke_id=0))
    return points if points else []

# Function to process multiple videos for a single gesture
def getPointsForMultipleVideos(video_list, label):
    templates = []
    for video in video_list:
        points = getPoints(video)
        if points:
            x_values = [p.x for p in points]
            y_values = [p.y for p in points]
            if max(x_values) - min(x_values) != 0 and max(y_values) - min(y_values) != 0:
                templates.append(Template(label, points))
    return templates

# Function to process multiple images for a single gesture
def getPointsForImages(image_list, label):
    templates = []
    for image in image_list:
        points = getPointsFromImage(image)
        if points:
            x_values = [p.x for p in points]
            y_values = [p.y for p in points]
            if max(x_values) - min(x_values) != 0 and max(y_values) - min(y_values) != 0:
                templates.append(Template(label, points))
    return templates

# Function to train templates and save them
def trainTemplates(save_path):
    templates = []

    # Define gestures with videos and images
    gesture_datasets = {
        "peace": {
            "videos": [
                "Dataset/peace/WhatsApp Video 2024-12-06 at 5.03.53 PM.mp4",
                "Dataset/peace/WhatsApp Video 2024-12-06 at 5.03.59 PM.mp4",
                "Dataset/peace/WhatsApp Video 2024-12-06 at 5.04.01 PM.mp4",
                "Dataset/peace/WhatsApp Video 2024-12-06 at 5.33.04 PM.mp4",
                "Dataset/peace/WhatsApp Video 2024-12-06 at 8.58.11 PM.mp4",
                "Dataset/peace/WhatsApp Video 2024-12-06 at 8.58.23 PM.mp4",
                "Dataset/peace/WhatsApp Video 2024-12-06 at 8.58.48 PM.mp4",
                "Dataset/peace/WhatsApp Video 2024-12-06 at 5.03.55 PM.mp4",
                "Dataset/peace/arrow1.mp4"
            ],
            "images": [
                "Dataset/peace/360_F_170257669_Sp2Nb7B6w8lk9qDKeOaeXHBeYBjz5D5N.jpg",
                "Dataset/peace/360_F_134076599_rOmYy3xuUBISfdhyX6VnUMUeaDFgKbg1.jpg"
            ]
        },
        "right": {
            "videos": [
                "Dataset/right/WhatsApp Video 2024-12-06 at 4.06.29 PM.mp4",
                "Dataset/right/WhatsApp Video 2024-12-06 at 4.06.42 PM.mp4",
                "Dataset/right/WhatsApp Video 2024-12-06 at 4.06.54 PM.mp4",
                "Dataset/right/WhatsApp Video 2024-12-06 at 4.07.20 PM.mp4",
                "Dataset/right/WhatsApp Video 2024-12-06 at 9.30.00 PM.mp4",
                "Dataset/right/WhatsApp Video 2024-12-06 at 9.30.09 PM.mp4",
                "Dataset/right/nr1.mp4",
                "Dataset/right/nr2.mp4"
            ],
            "images": [
                "Dataset/right/WhatsApp Image 2024-12-23 at 2.36.28 PM (1).jpeg",
                "Dataset/right/WhatsApp Image 2024-12-23 at 2.36.28 PM (2).jpeg",
                "Dataset/right/WhatsApp Image 2024-12-23 at 2.36.28 PM.jpeg",
                "Dataset/right/WhatsApp Image 2024-12-23 at 2.36.29 PM.jpeg",
                "Dataset/right/WhatsApp Image 2024-12-23 at 2.36.30 PM.jpeg"

            ]
        },
        "left": {
            "videos": [
                "Dataset/left/WhatsApp Video 2024-12-06 at 4.12.19 PM.mp4",
                "Dataset/left/WhatsApp Video 2024-12-06 at 4.12.33 PM (1).mp4",
                "Dataset/left/WhatsApp Video 2024-12-06 at 4.12.33 PM (2).mp4",
                "Dataset/left/WhatsApp Video 2024-12-06 at 4.12.33 PM.mp4",
                "Dataset/left/WhatsApp Video 2024-12-06 at 9.14.38 PM.mp4",
                "Dataset/left/WhatsApp Video 2024-12-06 at 9.14.41 PM.mp4",
                "Dataset/left/n1.mp4",
                "Dataset/left/n2.mp4",
                "Dataset/left/n3.mp4",
                "Dataset/left/n4.mp4"

            ],
            "images": [
                "Dataset/left/WhatsApp Image 2024-12-23 at 2.34.50 PM (1).jpeg",
                "Dataset/left/WhatsApp Image 2024-12-23 at 2.34.50 PM (2).jpeg",
                "Dataset/left/WhatsApp Image 2024-12-23 at 2.34.50 PM (3).jpeg",
                "Dataset/left/WhatsApp Image 2024-12-23 at 2.34.50 PM.jpeg",
                "Dataset/left/ni1.jpeg",
                "Dataset/left/ni2.jpeg"
            ]
        }
    }

    # Train templates for each gesture
    for label, data in gesture_datasets.items():
        templates.extend(getPointsForMultipleVideos(data["videos"], label))
        templates.extend(getPointsForImages(data["images"], label))

    # Save templates to disk
    with open(save_path, 'wb') as f:
        pickle.dump(templates, f)
    print(f"Templates saved to {save_path}")

# Function to load templates from file
def loadTemplates(save_path):
    if os.path.exists(save_path):
        with open(save_path, 'rb') as f:
            return pickle.load(f)
    return []

# Function to get points from a single frame
def getPointsFromFrame(frame):
    points = []

    with mp_hands.Hands(min_detection_confidence=0.9, min_tracking_confidence=0.8) as hands:
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(image)

        # Process hand landmarks
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                for landmark in hand_landmarks.landmark:
                    x, y = landmark.x, landmark.y
                    if not (np.isnan(x) or np.isnan(y)):
                        points.append(Point(x, y, stroke_id=0))
    return points

# Main program
template_file = "gesture_templates_final.pkl"
if not os.path.exists(template_file):
    trainTemplates(template_file)

templates = loadTemplates(template_file)

# Initialize Recognizer with loaded templates
recognizer = Recognizer(templates)

# Use live camera feed to recognize gestures
cap = cv2.VideoCapture(0)

with mp_hands.Hands(min_detection_confidence=0.9, min_tracking_confidence=0.8) as hands:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame from camera.")
            break

        points = getPointsFromFrame(frame)
        x_values = [p.x for p in points]
        y_values = [p.y for p in points]

        if points and (max(x_values) - min(x_values) != 0) and (max(y_values) - min(y_values) != 0):
            result = recognizer.recognize(points)

            if result:
                best_match = result[0]
                gesture_name = best_match
                cv2.putText(frame, f"Gesture: {gesture_name}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "No gesture detected", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow("Gesture Recognition", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
