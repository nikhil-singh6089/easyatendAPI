import firebase_admin
import os
from firebase_admin import credentials
from firebase_admin import db
from dotenv import load_dotenv

load_dotenv()

database_url = os.environ.get('DATABASE_URL')

# Initialize the Firebase Admin SDK
cred = credentials.Certificate('path/to/serviceAccountKey.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': database_url
})

# Get a database reference
#ref = db.reference('/path/to/data')

# Retrieve data from the database
#data = ref.get()

# Print the retrieved data
#print(data)