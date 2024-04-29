from pydantic import BaseModel
from typing import Optional, List
import uuid
from models import AttendanceUserData 

class ClassData(BaseModel):
    classId: str
    date: str
    classImageUrl: str
    className: str
    userName: str
    userId: str

class Attendance(BaseModel):
    attendanceId : str = str(uuid.uuid4())
    date : str
    userName : str
    className : str
    userId : str
    studentAttendanceList : List[AttendanceUserData] = []
    classId : str

class AttendanceUserData(BaseModel):
    userId: str
    studentName: str
    profilePictureUrl: str
    attendanceStatus: bool

class UserData:
    attendancePictureUrl : str
    profilePictureUrl : str
    role : str
    rollNumber : str
    userName : str
    uuid : str

class VerificationRequest(BaseModel):
    token: str
    email: str

# Verification response model
class VerificationResponse(BaseModel):
    verificationCode: Optional[str] = None