import os
import pypdf
import glob

def extract_all_text(folder, output_file):
    pdf_files = glob.glob(os.path.join(folder, "*.pdf"))
    all_text = ""
    
    print(f"Extraherar text från {len(pdf_files)} PDF-filer...")
    for pdf_path in pdf_files:
        name = os.path.basename(pdf_path)
        print(f"  Läser: {name}...")
        try:
            reader = pypdf.PdfReader(pdf_path)
            all_text += f"\n\n--- KÄLLA: {name} ---\n"
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    all_text += text + "\n"
        except Exception as e:
            print(f"  Kunde inte läsa {name}: {e}")
            
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(all_text)
    print(f"Klar! All RAG-text sparad till: {output_file} ({len(all_text)} tecken)")

if __name__ == "__main__":
    extract_all_text("rag_sources", "src/agents/rag_context.txt")
