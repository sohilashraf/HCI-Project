import cv2
import numpy as np
import dlib
import csv
import matplotlib.pyplot as plt
import seaborn as sns

cap = cv2.VideoCapture(1)
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

def pupil_position(eye_points, facial_landmarks, gray):
    eye_region = np.array([(facial_landmarks.part(point).x, facial_landmarks.part(point).y) for point in eye_points])
    min_x = np.min(eye_region[:, 0])
    max_x = np.max(eye_region[:, 0])
    min_y = np.min(eye_region[:, 1])
    max_y = np.max(eye_region[:, 1])
    
    eye = gray[min_y:max_y, min_x:max_x]
    _, threshold_eye = cv2.threshold(eye, 30, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(threshold_eye, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if contours and len(contours) > 0:
        contour = max(contours, key=cv2.contourArea)
        M = cv2.moments(contour)
        if M['m00'] != 0:
            cx = int(M['m10'] / M['m00'])  
            cy = int(M['m01'] / M['m00'])  
            return (min_x + cx, min_y + cy)  
    return (min_x + (max_x - min_x) // 2, min_y + (max_y - min_y) // 2)

def calibrate_gaze():
    calibration_points = [(0.5, 0.5), (0.1, 0.1), (0.9, 0.1), (0.1, 0.9), (0.9, 0.9)]  
    calibration_data = []
    for x, y in calibration_points:
        
        cv2.waitKey(2000)  
        
        _, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)
        for face in faces:
            landmarks = predictor(gray, face)
            left_pupil = pupil_position(range(36, 42), landmarks, gray)
            right_pupil = pupil_position(range(42, 48), landmarks, gray)
            screen_x = np.mean([left_pupil[0], right_pupil[0]]) / frame.shape[1] * 1366
            screen_y = np.mean([left_pupil[1], right_pupil[1]]) / frame.shape[0] * 768
            calibration_data.append(((x, y), (screen_x, screen_y)))
    return calibration_data

gaze_data = []

if __name__ == "__main__":
    calibration_data = calibrate_gaze()

    while True:
        _, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)

        for face in faces:
            landmarks = predictor(gray, face)
            left_pupil = pupil_position(range(36, 42), landmarks, gray)
            right_pupil = pupil_position(range(42, 48), landmarks, gray)
            screen_x = np.mean([left_pupil[0], right_pupil[0]]) / frame.shape[1] * 1920
            screen_y = np.mean([left_pupil[1], right_pupil[1]]) / frame.shape[0] * 1080
            gaze_data.append({"x":int(screen_x),"y": int(screen_y)})

        cv2.imshow("Frame", frame)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC key
            break

    cap.release()
    cv2.destroyAllWindows()
    
    # Create a 2D histogram of gaze data
    gaze_x = [gaze['x'] for gaze in gaze_data]
    gaze_y = [gaze['y'] for gaze in gaze_data]

    # Create a heatmap
    plt.figure(figsize=(10, 8))
    heatmap, xedges, yedges = np.histogram2d(gaze_x, gaze_y, bins=(50, 40), range=[[0, 1920], [0, 1080]])

    # Plotting the heatmap
    sns.heatmap(heatmap.T, cmap="hot", cbar=True, xticklabels=50, yticklabels=40)
    plt.title('Gaze Heatmap')
    plt.xlabel('Screen X')
    plt.ylabel('Screen Y')
    plt.show()

    # Optionally, save the gaze data
    with open('gaze_data.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Screen_X', 'Screen_Y'])
        for gaze in gaze_data:
            writer.writerow([gaze['x'], gaze['y']])

    print("Gaze data and heatmap generated.")
