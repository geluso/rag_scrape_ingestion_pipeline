import time
import requests
from document_payload import DocumentPayload
import html2text

def text_to_chunks(text):
    words = text.split()
    chunks = []
    while len(words) > 0:
        chunk = " ".join(words[:350])
        words = words[350:]
        chunks.append(chunk)
    return chunks

ngrok_url = "https://4cb3-2601-602-8b82-92b0-64d0-4b7b-a51a-85fb.ngrok-free.app"
indexed_chunks_url = "https://pets-to-policy-rag.vercel.app/api/indexed-chunks"

def main():
    with open("./urls/texas_law/labor_urls", "r") as f:
        for line in f:
            url = line.strip()
            response = requests.get(url)
            text = html2text.html2text(response.text)

            url_add_document = ngrok_url + "/add_document/"

            chunks = text_to_chunks(text)
            chunk_index = 0
            for chunk in chunks:
                # Create the chunk in the vector DB
                doc = DocumentPayload(url, chunk, chunk_index)
                vector_response = requests.post(url_add_document, json=doc.to_dict())
                
                # Create the chunk in the vercel indexed-chunks DB
                indexed_chunk_json = {
                    "url": url,
                    "chunkIndex": chunk_index,
                    "chunkText": chunk
                }
                vercel_response = requests.post(indexed_chunks_url, json=indexed_chunk_json)

                breakpoint()
                chunk_index += 1
                time.sleep(1)
                print("vector status:", vector_response.status_code)
                print("vercel status:", vercel_response.status_code)

if __name__ == "__main__":
    main()
    print('exit')