import os
import csv
import cv2
import pyttsx3
import numpy as np
import tkinter as tk
from time import time
import face_recognition
from datetime import datetime
from tkinter import messagebox

def detection():
    known_faces = {}
    cwd = os.getcwd()
    if 'faces' in os.listdir(cwd):
        faces_folder = os.path.join(cwd, 'faces')
        for face in os.listdir(faces_folder):
            name = face.split(".")[0]
            known_faces[name] = face_recognition.load_image_file(os.path.join("faces", face))

    known_face_encodings = {name: face_recognition.face_encodings(image)[0] for name, image in known_faces.items()}
    known_face_names = list(known_faces.keys())

    # Initialize CSV file
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H_%M_%S")
    csv_filename = f"attendance_{current_time}.csv"
    fieldnames = ['ID', 'Name', 'Date', 'Time In', 'Time Out', 'Status'] #list is created 

    video_capture = cv2.VideoCapture(0)
    attendance_record = {}
    last_capture_time = {}
    face_detected = {} 

    print("\nNow we will scan the face with every known face we have in the face directory...\n")

    with open(csv_filename, mode='w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        print("\nStarting....\n")

        no = 1

        while True:
            print("On it...\n")
            _, frame, small_frame, rgb_small_frame = None, None, None, None

            try:
                _, frame = video_capture.read()
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            except Exception as e:
                print('Camera is Disabled!')
                engine = pyttsx3.init()
                engine.setProperty('rate', 150)
                engine.setProperty('volume', 0.9)
                text = "Camera is Diabled!"
                engine.say(text)
                engine.runAndWait()

            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            name = None

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                print(f"Tyring face {no}")
                matches = face_recognition.compare_faces(list(known_face_encodings.values()), face_encoding)
                face_distances = face_recognition.face_distance(list(known_face_encodings.values()), face_encoding)

                if True in matches:
                    best_match_index = np.argmin(face_distances)
                    name = known_face_names[best_match_index]
                    print("Matching")
                    # Check if it's time to capture attendance for this person
                    current_time = time()
                    if name not in last_capture_time or (current_time - last_capture_time[name]) > 30:
                        print("The Guy is present!")

                        if name not in attendance_record:
                            attendance_record[name] = {'ID': best_match_index + 1, 'Name': name, 'Date': datetime.now().strftime("%Y-%m-%d"),
                                                    'Time In': datetime.now().strftime("%H:%M:%S"), 'Time Out': '', 'Status': 'Present'}
                            last_capture_time[name] = current_time
                            writer.writerow(attendance_record[name])
                            print('Yes 1')
                        else:
                            attendance_record[name]['Status'] = 'Present'
                            print('No 1')
                        
                        if name not in face_detected or not face_detected[name]:
                            attendance_record[name]['Time In'] = datetime.now().strftime("%H:%M:%S")
                            print('Yes 2')
                        face_detected[name] = True

                        cv2.rectangle(frame, (left * 4, top * 4), (right * 4, bottom * 4), (0, 0, 255), 2)
                        cv2.putText(frame, f"{name} - Present", (left * 4 + 6, bottom * 4 - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

                        '''
                            Here we will be comfirming that the student is already present, 
                            Thus we will speak '{Student_name} Present!'
                        '''
                        
                        engine = pyttsx3.init()
                        engine.setProperty('rate', 150)
                        engine.setProperty('volume', 0.9)
                        text = f"{name} Present!"
                        engine.say(text)
                        engine.runAndWait()

                    else:
                        last_capture_time[name] = current_time
                        '''
                            Here the student is already marked its attendence and trying to make another one,
                            So we will speak, '{Student_name} already marked!'
                        '''

                        engine = pyttsx3.init()
                        engine.setProperty('rate', 150)
                        engine.setProperty('volume', 0.9)
                        text = f"{name} your attendance is already marked!"
                        engine.say(text)
                        engine.runAndWait()
                else:
                    print('Maybe the Guy is not Present')
                    if name in face_detected and face_detected[name]:
                        print("The guy is not present")
                        attendance_record[name]['Time Out'] = datetime.now().strftime("%H:%M:%S")
                        writer.writerow(attendance_record[name])
                        del attendance_record[name]
                    face_detected[name] = False

                    engine = pyttsx3.init()
                    engine.setProperty('rate', 150)
                    engine.setProperty('volume', 0.9)
                    text = "Unknown Student!"
                    engine.say(text)
                    engine.runAndWait()

                no += 1

            cv2.imshow("Attendance", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        csv_file.close()

    video_capture.release()
    cv2.destroyAllWindows()

def exit_app():
    root.destroy()

def exit_fullscreen(event=None):
    root.attributes("-fullscreen", False)

root = tk.Tk()
root.title("Attendence Tracking App (BETA)")

root.geometry("800x600")
root.state("zoomed")

# Welcome_text = tk.Label(root, text="WELCOME TO ATTENDENCE TRACKING APP", font=("Arial", 14))

label = tk.Label(root, text="WELCOME TO ATTENDENCE TRACKING APP", anchor=tk.CENTER, bg="lightblue", height=3, width=30, bd=3, font=("Arial", 16, "bold"), cursor="hand2", fg="black", padx=15, pady=15, justify=tk.CENTER, relief=tk.RAISED, underline=0, wraplength=250).pack(pady=20)

exit_button = tk.Button(root, text="Exit", command=exit_app, font=("Arial", 14)).pack(padx=5, pady=5)

exit_button = tk.Button(root, text="Start Detection", command=detection, font=("Arial", 14)).pack(padx=5, pady=5)

root.bind("<Escape>", exit_fullscreen)
root.mainloop()