from fastapi import FastAPI, HTTPException
import firebase_admin
import uvicorn
import os
import string
from typing import List
from dotenv import load_dotenv
from firebase_admin import credentials
from firebase_admin import db
import random
from emailsender import send_email
from models import ClassData , VerificationRequest, VerificationResponse, AttendanceUserData, Attendance
from firebase import buildUpBeforeVerification, deleteImagesInFolder, delete_all_folders
from ai import verify_extracted_faces

load_dotenv()

database_url = os.environ.get('DATABASE_URL')
sender_email = os.environ.get('SENDER_EMAIL')
sender_password = os.environ.get('SENDER_PASSWORD')
COMMON_TOKEN = os.environ.get('secret_key')
database_url = os.environ.get('DATABASE_URL')

# Initialize the Firebase Admin SDK
cred = credentials.Certificate('easyattend.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': database_url
})


subject = "Email Verification Code Easyattend"

def generate_random_number():
    return random.randint(10000, 99999)

def email_sender(receiver_email, code):
    #code = generate_random_number()
    body = f"Your verification code is: {code}"
    send_email(sender_email, receiver_email, sender_password, subject, body)

def wrapUp():
    # wrap up of a api request

    current_directory = os.getcwd()
    attendance_classImage_directory = os.path.join(current_directory, "ClassImage")
    attendance_classImageFaces_directory = os.path.join(current_directory, "DetectedFaces")
    attendance_classStudentFaces_directory = os.path.join(current_directory, "ClassStudentFaces")
    deleteImagesInFolder(attendance_classImage_directory)
    deleteImagesInFolder(attendance_classImageFaces_directory)
    delete_all_folders(attendance_classStudentFaces_directory)


app = FastAPI()

@app.post("/verify", response_model=VerificationResponse)
def verify_email(request: VerificationRequest):
    if request.token != COMMON_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")
    if request.email is None or request.email == "":
        raise HTTPException(status_code=400, detail="Email is required")
    
    print("Email: ", request.email)

    # Generate a random verification code
    verificationCode = ''.join(random.choices(string.digits, k=6))

    # Send the verification code to the email
    email_sender(request.email, verificationCode)

    return VerificationResponse(verificationCode=verificationCode)

@app.post("/attendance")
def create_class(class_data: ClassData):
    # Convert the Pydantic model to a dictionary
    data = class_data.model_dump()
    print(data)

    classImageUrl = data["classImageUrl"]
    classId = data["classId"]

    current_directory = os.getcwd()
    attendance_classImageFaces_directory = os.path.join(current_directory, "DetectedFaces")
    studentAttendanceData : List[AttendanceUserData] = []
    
    verification_image_paths = buildUpBeforeVerification(classId, classImageUrl)
    studentAttendanceData = verify_extracted_faces(attendance_classImageFaces_directory, verification_image_paths)
    # Create a new Classes object
    #attendanceId = uuid.uuid4().hex
    #print(attendanceId)
    #uuid issue solved in model.py using str(uuid.uuid4())
    new_attendance = Attendance(
        date=data["date"],
        userName=data["userName"],
        className=data["className"],
        userId=data["userId"],
        studentAttendanceList=studentAttendanceData,
        classId=data["classId"]
    )
    print(new_attendance.attendanceId)  
    ref = db.reference(f'Attendance/{new_attendance.attendanceId}')
    ref.set(new_attendance.model_dump())
    wrapUp()
    return {"message": "attendance updated successfully"}



@app.get("/")
def read_root():
    return {"Hello": "World"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

# create a .env file in the root directory of the project and 
# add the following environment variables:
#
# DATABASE_URL=
# SENDER_EMAIL = 
# SENDER_PASSWORD = 
# secret_key = 

