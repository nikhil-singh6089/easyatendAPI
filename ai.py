#FINAL WORKING EXTRACTION AND VERIFICATION C0DE!

import os
import cv2
from deepface import DeepFace
from retinaface import RetinaFace
from firebase_admin import db
from models import AttendanceUserData

current_directory = os.getcwd()
attendance_classImageFaces_directory = os.path.join(current_directory, "DetectedFaces")
output_dir = "DetectedFaces"  # Replace with your desired output directory
extracted_faces_dir = attendance_classImageFaces_directory  # Directory path of the extracted faces


def save_extracted_faces(image_path, output_dir, filename_prefix="extracted_face_", start_number=1):
  """
  Extracts and saves all faces detected in an image to a separate directory.

  Args:
      image_path: The path to the image containing faces.
      output_dir: The directory path to store the extracted faces.
      filename_prefix: The prefix for the filenames (default: "extracted_face_").
      start_number: The starting number for the filename sequence (default: 1).
  """

  # Create the output directory if it doesn't exist
  os.makedirs(output_dir, exist_ok=True)

  # Load the image
  image = cv2.imread(image_path)

  # Face detection using DeepFace (replace with your actual detector)
  results = RetinaFace.detect_faces(image)

  # Extract and save each face
  i = start_number
  for key in results.keys():
    identity = results[key]
    facial_area = identity["facial_area"]

    # Extract face region using slicing based on rectangle coordinates
    face_image = image[facial_area[1]:facial_area[3], facial_area[0]:facial_area[2]]

    # Save the extracted face
    saved_filepath = save_extracted_face(face_image, output_dir, filename_prefix, i)
    print(f"Face #{i} saved to: {saved_filepath}")
    i += 1

def save_extracted_face(face_image, output_dir, filename_prefix="extracted_face_", start_number=1):
  """
  Saves a single face image to a separate directory.

  Args:
      face_image: The NumPy array representing the extracted face image.
      output_dir: The directory path to store the extracted face.
      filename_prefix: The prefix for the filenames (default: "extracted_face_").
      start_number: The starting number for the filename sequence (default: 1).

  Returns:
      The full path of the saved image file.
  """

  # Find the next available numbered filename
  filename = f"{filename_prefix}{start_number}.jpg"
  filepath = os.path.join(output_dir, filename)
  while os.path.exists(filepath):
    start_number += 1
    filename = f"{filename_prefix}{start_number}.jpg"
    filepath = os.path.join(output_dir, filename)

  # Save the face image using OpenCV (assuming it's a NumPy array)
  cv2.imwrite(filepath, face_image)

  return filepath




def verify_extracted_faces(extracted_faces_dir, verification_image_paths, tolerance=0.6):
  """
  Verifies extracted faces against provided images using DeepFace and prints results.

  Args:
      extracted_faces_dir: The directory path containing extracted faces.
      verification_image_paths: A list of paths to images for verification.
      tolerance: The threshold for considering a face a match (default: 0.6).
  """
  studentAttendanceData = []
  # Process each verification image
  for verification_image_path in verification_image_paths:
    # Load the verification image
    verification_image = cv2.imread(verification_image_path)
    userId = getUserIdFromVerificationPath(verification_image_path)
    userData = getUserData(userId)
    verified_faces_ids = []  # List to store verified faces (filename, distance)

    # Process each extracted face image
    for filename in os.listdir(extracted_faces_dir):
      if filename.endswith(".jpg") or filename.endswith(".png"):  # Check for image extensions
        filepath = os.path.join(extracted_faces_dir, filename)
        extracted_face = cv2.imread(filepath)

        # Face verification using DeepFace
        result = DeepFace.verify(verification_image, extracted_face, enforce_detection=False)
        is_verified = result["verified"]
        distance = result["distance"]

        # Add verified faces to the list #updated to attendance list
        if is_verified and distance <= tolerance:
          #verified_faces.append((filename, distance))
          userData.attendanceStatus = True
          studentAttendanceData.append(userData)

    userData.attendanceStatus = False
    studentAttendanceData.append(userData)
    # Print results for the current verification image
    # image_name = os.path.basename(verification_image_path)
    # if verified_faces:
    #   print(f"Results for '{image_name}':")
    #   for filename, distance in verified_faces:
    #     print(f"- {filename} (Distance: {distance:.2f})")
    # else:
    #   print(f"No faces verified in '{extracted_faces_dir}' against '{image_name}'.")

  return studentAttendanceData
  

def getUserData(userId):
    ref = db.reference(f'Users/{userId}')
    data = ref.get()

    userName = data.get('userName',"")
    profilePictureUrl = data.get('profilePictureUrl',"")
    
    userData = AttendanceUserData(userId=userId, studentName=userName, profilePictureUrl=profilePictureUrl, attendanceStatus=False)

    return userData

def getUserIdFromVerificationPath(verification_path):
  filename = verification_path.split('/')[-1]
  image_name = filename.split('.')[0]
  return image_name

# if __name__ == "__main__":
#   image_path = "/content/facerec_2.jpg" #Class Photo path
#   output_dir = "extracted_faces"  # Replace with your desired output directory
#   save_extracted_faces(image_path, output_dir)
#   print("Faces extracted.")
#   extracted_faces_dir = "/content/extracted_faces"  # Directory path of the extracted faces
#   verification_image_paths = ["/content/steven_yeun_1.jpg", "/content/andrew_3.jpg"]  # Image paths for the verification images
#   tolerance = 0.8  
#   verify_extracted_faces(extracted_faces_dir, verification_image_paths, tolerance)

# name = getUserIdFromVerificationPath('/home/nikhil/Projects/easyattendAPI/ClassStudentFaces/20BCE10001/20BCE10001.jpg')
# print(name)
