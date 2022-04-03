import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
import pickle
import time
from datetime import datetime
import threading

#if modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

sheep_folder_id = '1UOhj83ehUMeUS7fncrrw1qJrPBPIu7Le'
delete_timeout = 60 * 60 * 24 * 7

#connects to google drive and authenticates
def get_gdrive_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    # return Google Drive API service
    print('Auth successful')
    return build('drive', 'v3', credentials=creds)

# authenticate account
service = get_gdrive_service()   

#creates file_name under folder_name
def upload_file(folder_id, file_name):
    file_metadata = {
        "name": os.path.basename(file_name),
        "parents": [folder_id]
    }

    try:
        print("Uploading...")
        media = MediaFileUpload(file_name, resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f"File {file_metadata['name']} uploaded successfully, id: {file.get('id')}")
        return True
    except Exception as e:
        print(f"An error occurred during the upload! Will skip this file: {file_metadata['name']}")
        print('----- Exception -----')
        print(e)
        return False

class FileState:
    path = ""
    time = time.time()
    duration = 0
    tried_upload = False
    def __init__(self, path, duration):
        self.path = path
        self.duration = duration

def load_state():
    if os.path.exists('state.pickle'):
        with open('state.pickle', 'rb') as statefile:
            return pickle.load(statefile)
    else:
        return []

state = load_state()

def save_state():
    with open('state.pickle', 'wb') as statefile:
            pickle.dump(state, statefile)

def add_file(path, duration):
    state.append(FileState(path, duration))
    save_state()

class Uploader(threading.Thread):
    def run(self):
        main()

def main():
    for file in state[::-1]:
        if time.time() - file.time > delete_timeout:
            os.system(f'rm -rf {file.path}')
            state.remove(file)
            continue
        file.tried_upload = True
        if upload_file(sheep_folder_id, file.path):
            os.system(f'rm -rf {file.path}')
            state.remove(file)
        save_state()

if __name__ == '__main__':
    u = Uploader()
    u.start()


