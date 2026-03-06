import os
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import pickle

def get_drive_service():
    token_path = r'C:\Jeeves_ADHD_Butlern\token.pickle'
    if not os.path.exists(token_path):
        print("token.pickle saknas! Kör GoogleBridge först.")
        return None
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)
    return build('drive', 'v3', credentials=creds)

def find_notebook_files(folder_id=None):
    service = get_drive_service()
    if not service: return
    
    # NotebookLM filer sparas ofta i en specifik mapp eller har "Notebook" i namnet
    query = "mimeType = 'application/pdf' or mimeType = 'application/vnd.google-apps.document'"
    if folder_id:
        query = f"'{folder_id}' in parents and ({query})"
    
    results = service.files().list(
        q=query,
        pageSize=10, 
        fields="nextPageToken, files(id, name, mimeType)"
    ).execute()
    items = results.get('files', [])

    if not items:
        print('Inga relevante filer hittades i din Google Drive.')
    else:
        print('Filer som kan tillhöra din RAG:')
        for item in items:
            print(f"{item['name']} ({item['id']})")

if __name__ == "__main__":
    find_notebook_files()
