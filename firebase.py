import firebase_admin
from firebase_admin import credentials
import os
import requests
import shutil
from firebase_admin import db
from dotenv import load_dotenv
from ai import save_extracted_faces

load_dotenv()

# database_url = os.environ.get('DATABASE_URL')

# # Initialize the Firebase Admin SDK
# cred = credentials.Certificate('easyattend.json')
# firebase_admin.initialize_app(cred, {
#     'databaseURL': database_url
# })

verification_image_paths = []

def getClassImage(imageUrl):
    response = requests.get(imageUrl)
    if response.status_code == 200:
        # Get the filename from the URL
        filename = "classImage.jpg"
        current_directory = os.getcwd()

        attendance_classImage_directory = os.path.join(current_directory, "ClassImage")
        
        # Define the path to save the image
        image_path = os.path.join(attendance_classImage_directory, filename)
        
        # Save the image to the specified folder
        with open(image_path, "wb") as file:
            file.write(response.content)
            
        print("Image downloaded successfully.")
        return image_path
    else:
        print("Failed to download the image.")
        return None


def deleteImagesInFolder(folder_path):
    """
    Delete all image files in a specified folder.

    Args:
    - folder_path (str): The path to the folder containing the image files.

    Returns:
    - bool: True if all image files were deleted successfully, False otherwise.
    """
    try:
        # Check if the folder exists
        if os.path.exists(folder_path):
            # Iterate over all files in the folder
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                # Check if the file is an image (you may need to adjust this condition based on your file naming conventions)
                if os.path.isfile(file_path) and filename.endswith(('.jpg', '.jpeg', '.png', '.gif', '.py')):
                    # Delete the image file
                    os.remove(file_path)
                    print(f"Deleted: {filename}")
            print("All images deleted successfully.")
            return True
        else:
            print("Folder does not exist.")
            return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def delete_all_folders(folder_path):
    """
    Delete all folders within the specified folder.

    Args:
    - folder_path (str): Path to the folder containing folders to be deleted.

    Returns:
    - None
    """
    # Get the list of items (folders and files) in the specified folder
    items = os.listdir(folder_path)

    # Iterate through each item
    for item in items:
        # Construct the full path of the item
        item_path = os.path.join(folder_path, item)
        
        # Check if the item is a directory (folder)
        if os.path.isdir(item_path):
            # Delete the folder and its contents recursively
            try:
                shutil.rmtree(item_path)
                print(f"Deleted folder and its contents: {item_path}")
            except OSError as e:
                print(f"Failed to delete folder and its contents: {item_path} - {e}")

def createStudentFolderAndImage(folder_name):

    """
    Create a folder for user images and download the image inside it.

    Args:
    - folder_name (str): The name of the folder to create.

    Returns:
    - bool: True if the folder was created successfully or already exists, False otherwise.
    """

    # Get a database reference
    ref = db.reference(f'Users/{folder_name}')

    # Retrieve data from the database
    data = ref.get()

    attendanceUrl = data.get('attendancePictureUrl', "")
    print(attendanceUrl)

    current_directory = os.getcwd()

    attendance_faces_directory = os.path.join(current_directory, "ClassStudentFaces")

    folder_path = os.path.join(attendance_faces_directory, folder_name)

    if not os.path.exists(folder_path):
        # Create the folder
        os.mkdir(folder_path)
        print("Folder created successfully.")
        response = requests.get(attendanceUrl)
        if response.status_code == 200:
        # Get the filename from the URL
            filename = f"{folder_name}.jpg"
            
            # Define the path to save the image
            image_path = os.path.join(folder_path, filename)
            verification_image_paths.append(image_path)
            
            # Save the image to the specified folder
            with open(image_path, "wb") as file:
                file.write(response.content)
                
            print("Image downloaded successfully.")
        else:
            print("Failed to download the image.")

    else:
        print("Folder already exists.")


def getClassStudents(classId):
    """
    Retrieve the list of students for a given class from the Firebase Realtime Database.

    Args:
    - classId (str): The ID of the class to retrieve students for.

    Returns:
    - list: A list of student IDs for the specified class.
    """
    try:
        # Get a database reference to the specified class
        ref = db.reference(f'Classes/{classId}')
        
        studentData = ref.get()
        
        if studentData is None:
            print("No students found for the specified class.")
            return []
        else:
            # Convert the dictionary keys to a list
            classStudentIds = studentData.get('classStudents', [])
            print(f"Retrieved students for class {classId}: {classStudentIds}")
            return classStudentIds
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    
def putStudentImageInFolder(classId):

    classStudentIds = getClassStudents(classId)
    for studentId in classStudentIds:
        createStudentFolderAndImage(studentId)

def buildUpBeforeVerification(classId,classImageUrl):

    current_directory = os.getcwd()
    attendance_classImageFaces_directory = os.path.join(current_directory, "DetectedFaces")
    imagePath = getClassImage(classImageUrl)
    save_extracted_faces(imagePath, attendance_classImageFaces_directory, "classImageFace_",1)
    putStudentImageInFolder(classId)
    return verification_image_paths


    
#getClassStudents('76fe25c2-063e-4765-b30d-8817bcc2d253') working 
#buildUpBeforeVerification('76fe25c2-063e-4765-b30d-8817bcc2d253','https://firebasestorage.googleapis.com/v0/b/advnotesapp-c1f16.appspot.com/o/AIImages%2F2024-04-30%2F76fe25c2-063e-4765-b30d-8817bcc2d253?alt=media&token=1dd6529a-c043-4e7c-a4d0-797a5ff28f77') #working
#getClassImage('https://firebasestorage.googleapis.com/v0/b/advnotesapp-c1f16.appspot.com/o/AIImages%2F2024-04-30%2F76fe25c2-063e-4765-b30d-8817bcc2d253?alt=media&token=1dd6529a-c043-4e7c-a4d0-797a5ff28f77')
#folder_path = "/home/nikhil/Projects/easyattendAPI/DetectedFaces"
#folder_path = "/home/nikhil/Projects/easyattendAPI/ClassStudentFaces"
#deleteImagesInFolder(folder_path)
#delete_all_folders("/home/nikhil/Projects/easyattendAPI/ClassStudentFaces")
#createStudentFolderAndImage('20BCE10001')
#putStudentImageInFolder('76fe25c2-063e-4765-b30d-8817bcc2d253') #working
#print(verification_image_paths)
