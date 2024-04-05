import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Initialize the Firebase Admin SDK
cred = credentials.Certificate('path/to/serviceAccountKey.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://your-project-id.firebaseio.com'
})

# Get a database reference
ref = db.reference('/path/to/data')

# Retrieve data from the database
data = ref.get()

# Print the retrieved data
print(data)