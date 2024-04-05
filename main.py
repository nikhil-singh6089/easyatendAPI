from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from jose import JWTError, jwt
import uvicorn
import os
import string
from dotenv import load_dotenv
import random
from emailsender import send_email

load_dotenv()

sender_email = os.environ.get('SENDER_EMAIL')
sender_password = os.environ.get('SENDER_PASSWORD')
COMMON_TOKEN = os.environ.get('secret_key')

subject = "Email Verification Code Easyattend"

def generate_random_number():
    return random.randint(10000, 99999)

def email_sender(receiver_email, code):
    #code = generate_random_number()
    body = f"Your verification code is: {code}"
    send_email(sender_email, receiver_email, sender_password, subject, body)


app = FastAPI()

class VerificationRequest(BaseModel):
    token: str
    email: str

# Verification response model
class VerificationResponse(BaseModel):
    verificationCode: Optional[str] = None

@app.post("/verify", response_model=VerificationResponse)
def verify_email(request: VerificationRequest):
    if request.token != COMMON_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")
    if request.email is None:
        raise HTTPException(status_code=400, detail="Email is required")
    
    print("Email: ", request.email)

    # Generate a random verification code
    verificationCode = ''.join(random.choices(string.digits, k=6))

    # Send the verification code to the email
    email_sender(request.email, verificationCode)

    return VerificationResponse(verificationCode=verificationCode)

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

