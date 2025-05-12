import cv2
import numpy as np
import face_recognition
import pandas as pd
from datetime import datetime

print("Libraries imported successfully!")

def load_known_faces_and_names():
    known_face_encodings = []
    known_face_names = []

    # Load images and their corresponding names
    images = ['person1.jpg','person2.jpg']  # Add your actual image filenames
    names = ['Mano','Sharmila']  # Corresponding names

    for img, name in zip(images, names):
        image = face_recognition.load_image_file(img)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            known_face_encodings.append(encodings[0])
            known_face_names.append(name)
        else:
            print(f"Warning: No face found in {img}")
    return known_face_encodings, known_face_names

def mark_attendance(name):
    try:
        with open('attendance.csv', 'r+') as f:
            myDataList = f.readlines()
            nameList = [line.split(',')[0] for line in myDataList]
            if name not in nameList:
                now = datetime.now()
                dtString = now.strftime('%Y-%m-%d %H:%M:%S')
                f.writelines(f'\n{name},{dtString}')
    except FileNotFoundError:
        with open('attendance.csv', 'w') as f:
            now = datetime.now()
            dtString = now.strftime('%Y-%m-%d %H:%M:%S')
            f.write(f'{name},{dtString}\n')

# Start webcam
video_capture = cv2.VideoCapture(0)
known_face_encodings, known_face_names = load_known_faces_and_names()

while True:
    ret, frame = video_capture.read()
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)

        if face_distances.size > 0:
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
                mark_attendance(name)

        # Draw a box and label
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    cv2.imshow('Video', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
