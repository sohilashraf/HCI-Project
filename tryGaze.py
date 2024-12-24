import cv2
import dlib
import pandas as pd
import numpy as np

# Initialize dlib's face detector and the shape predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")  # Ensure this file is available

def midpoint(p1, p2):
    return (p1.x + p2.x) // 2, (p1.y + p2.y) // 2

def get_gaze_direction(left_pupil, right_pupil):
    # Calculate the horizontal midpoint between the two pupils
    midpoint_x = (left_pupil[0] + right_pupil[0]) // 2
    
    # Compare with the center of the frame (or face region)
    frame_center_x = 320  # You can adjust this based on your camera resolution (e.g., 640x480)

    # Define a threshold for determining center vs left/right gaze
    gaze_threshold = 50  # Adjust as necessary
    
    if abs(left_pupil[0] - right_pupil[0]) < 20:  # If the pupils are close together
        return "Looking center"
    elif midpoint_x < (frame_center_x - gaze_threshold):
        return "Looking left"
    elif midpoint_x > (frame_center_x + gaze_threshold):
        return "Looking right"
    else:
        return "Looking center"


# Prepare DataFrame to log data
log_data = []

# Start capturing video
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    for face in faces:
        landmarks = predictor(gray, face)

        # Get left and right eye landmarks
        left_eye = [landmarks.part(i) for i in range(36, 42)]
        right_eye = [landmarks.part(i) for i in range(42, 48)]

        # Compute pupil positions
        left_pupil = midpoint(left_eye[0], left_eye[3])
        right_pupil = midpoint(right_eye[0], right_eye[3])

        # Log the data
        direction = get_gaze_direction(left_pupil, right_pupil)
        log_data.append({
            "Left Pupil X": left_pupil[0],
            "Left Pupil Y": left_pupil[1],
            "Right Pupil X": right_pupil[0],
            "Right Pupil Y": right_pupil[1],
            "Gaze Direction": direction
        })

        # Draw eye landmarks
        for i in range(36, 48):
            cv2.circle(frame, (landmarks.part(i).x, landmarks.part(i).y), 1, (0, 255, 0), -1)

        # Highlight pupils
        cv2.circle(frame, left_pupil, 3, (0, 255, 0), -1)
        cv2.circle(frame, right_pupil, 3, (0, 255, 0), -1)

        # Gaze direction
        cv2.putText(frame, direction, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Display pupil coordinates
        cv2.putText(frame, f"Left pupil: {left_pupil}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(frame, f"Right pupil: {right_pupil}", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    cv2.imshow("Pupil and Gaze Tracking", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Save data to Excel when the loop ends
if log_data:  # Check if any data has been logged
    df = pd.DataFrame(log_data)
    df.to_excel("pupil_gaze_data.xlsx", index=False)
    print("Data saved to pupil_gaze_data.xlsx")
else:
    print("No data was recorded.")

cap.release()
cv2.destroyAllWindows()
