import os
import io
import pickle
import argparse
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.credentials import Credentials

from utils.google_bridge import GoogleBridge

def get_drive_service():
    bridge = GoogleBridge()
    return build('drive', 'v3', credentials=bridge.creds)

def download_file(file_id, file_name, destination_folder):
    service = get_drive_service()
    if not service: return
    
    # Handle Google Docs by exporting to PDF
    request = service.files().get(fileId=file_id, fields="mimeType").execute()
    mime_type = request.get('mimeType', '')
    
    if 'vnd.google-apps.' in mime_type:
        print(f"  Expoterar Google Doc: {file_name} -> PDF")
        request = service.files().export_media(fileId=file_id, mimeType='application/pdf')
        if not file_name.endswith('.pdf'): file_name += '.pdf'
    else:
        print(f"  Laddar ner: {file_name}")
        request = service.files().get_media(fileId=file_id)
        
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        # print(f"Download {int(status.progress() * 100)}%.")
    
    dest_path = os.path.join(destination_folder, file_name)
    with open(dest_path, 'wb') as f:
        f.write(fh.getvalue())
    print(f"  Sparad till: {dest_path}")

def find_and_download(queries, dest_folder):
    service = get_drive_service()
    if not service: return
    
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
        
    for query_name in queries:
        print(f"Söker efter: {query_name}...")
        # Exact name search or partial
        q = f"name contains '{query_name}' and (mimeType = 'application/pdf' or mimeType contains 'vnd.google-apps')"
        results = service.files().list(q=q, fields="files(id, name, mimeType)").execute()
        files = results.get('files', [])
        
        if not files:
            print(f"  Hittade inga matchningar för '{query_name}'")
            continue
            
        for f in files:
            download_file(f['id'], f['name'], dest_folder)

if __name__ == "__main__":
    import re
    
    rag_file = r"C:\Jeeves_ADHD_Butlern\rag_files.txt"
    if not os.path.exists(rag_file):
        print(f"Hittade inte {rag_file}")
    else:
        with open(rag_file, 'r', encoding='utf-8') as f:
            filer = [line.strip() for line in f if line.strip() and not line.startswith("TOTALT:")]
        
        # Unika filer för att undvika dubbeljobb
        unika_filer = list(set(filer))
        print(f"Startar nedladdning av {len(unika_filer)} källor...")
        find_and_download(unika_filer, "rag_sources")

