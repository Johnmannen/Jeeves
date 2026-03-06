import os
import io
import pickle
import argparse
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.credentials import Credentials
import re

# Same logic as before but optimized for a smaller list
from utils.google_bridge import GoogleBridge

def get_drive_service():
    bridge = GoogleBridge()
    return build('drive', 'v3', credentials=bridge.creds)

def download_file(file_id, file_name, destination_folder):
    service = get_drive_service()
    if not service: return
    
    # Handle filename characters for Windows
    clean_name = re.sub(r'[\/:*?"<>|]', '_', file_name)
    dest_path = os.path.join(destination_folder, clean_name)
    
    if os.path.exists(dest_path):
        print(f"  Skippar: {clean_name} (redan nedladdad)")
        return

    request = service.files().get(fileId=file_id, fields="mimeType").execute()
    mime_type = request.get('mimeType', '')
    
    if 'vnd.google-apps.' in mime_type:
        print(f"  Expoterar Google Doc: {file_name} -> PDF")
        request = service.files().export_media(fileId=file_id, mimeType='application/pdf')
        if not dest_path.endswith('.pdf'): dest_path += '.pdf'
    else:
        print(f"  Laddar ner: {file_name}")
        request = service.files().get_media(fileId=file_id)
        
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    
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
        q = f"name contains '{query_name}'"
        results = service.files().list(q=q, fields="files(id, name, mimeType)").execute()
        files = results.get('files', [])
        
        if not files:
            print(f"  Hittade inga matchningar")
            continue
            
        # Download the first match found
        download_file(files[0]['id'], files[0]['name'], dest_folder)

if __name__ == "__main__":
    viktiga_filer = [
        "1-Projektblueprint_ Exekutiv v1.0 – Master-Prompt.pdf",
        "Jeeves: Projektplan",
        "Jeeves: To-Do-lista",
        "1-Exekutiv: AI-assistenten för kognitivt stöd",
        "1-Neurodesign Kravspecifikation",
        "ADHD (aktivitets- och uppmärksamhetsstörning)",
        "ADHD - Kunskapsstöd för vårdgivare",
        "Systembiologiska och kliniska perspektiv på vuxen-ADHD",
        "AI som kognitiv protes",
        "Architectural Evolution and Ecosystem Analysis",
        "Your Ultimate Interoceptive Exposure",
        "5 olika Metoder för Biologisk Stressreglering",
        "Interoceptiv exponering: Metoder",
        "9 Clear Signs Of Executive Dysfunction",
        "Why Standard Productivity Systems Fail ADHD Brains",
        "toward neurodivergent-aware productivity",
        "Executive Function Disorder & ADHD - ADDA",
        "Riktlinje Adhd 2025",
        "Cognitive_Prosthesis_AI.pdf",
        "Total Plan ADHD-Jeeves multiagent solution 1.0",
        "checklista för ADHD hos barn - 15 vanliga symtom",
        "checklista: ADHD-symtom hos vuxna",
        "The impact of high-intensity interval training on anxiety: a scoping review",
        "Transforming mental health: The future of personalized psychobiotics",
        "Psychobiotics as an Adjunctive Therapy"
    ]
    find_and_download(viktiga_filer, "rag_sources")
