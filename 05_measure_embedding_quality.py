import os
import requests
import html2text

from langchain_community.embeddings import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from queries import queries

CHUNK_SIZE = 100
url = "https://statutes.capitol.texas.gov/Docs/LA/htm/LA.301.htm"

embedding_bert = "nlpaueb/legal-bert-base-uncased"
embedding_openai = "text-embedding-3-large"

doc_id_to_texas_code_section = {
    "248334430092713580": "Sec. 301.081.",
    "7962335798518110197": "Sec. 301.085.",
    "-9126909904113458633": "Sec. 301.042.",
    "8092507351456004109": "Sec. 301.045.",
    "-3347123552670936071": "Sec. 301.003.",
    "4093232429982980593": "Sec. 301.156."
}

def create_vectorstore(name, model):
    embeddings = HuggingFaceEmbeddings(model_name=model) if name == "bert" else OpenAIEmbeddings(model=model, openai_api_key=os.environ.get("OPENAI_API_KEY"))
    persist_directory = f"./chroma_db_{name}_{CHUNK_SIZE}"
    return Chroma(
        embedding_function=embeddings,
        persist_directory=persist_directory
    )

def text_to_chunks(text):
    words = text.split()
    chunks = []
    while len(words) > 0:
        chunk = " ".join(words[:CHUNK_SIZE])
        words = words[CHUNK_SIZE:]
        chunks.append(chunk)
    return chunks

def init_dbs(bert_vectors, openai_vectors):
    response = requests.get(url)
    text = html2text.html2text(response.text)

    chunks = text_to_chunks(text)
    for chunk in chunks:
        chunk_id = str(hash(chunk))
        lang_doc = Document(id=chunk_id, page_content=chunk)

        bert_docs = bert_vectors.get_by_ids([chunk_id])
        if len(bert_docs) == 0:
            print("adding bert", chunk_id)
            bert_vectors.add_documents(documents=[lang_doc])

        openai_docs = openai_vectors.get_by_ids([chunk_id])
        if len(openai_docs) == 0:
            print("adding openai", chunk_id)
            openai_vectors.add_documents(documents=[lang_doc])


def main():
    bert_vectors = create_vectorstore("bert", embedding_bert)
    openai_vectors = create_vectorstore("openai", embedding_openai)

    id_to_doc = {}

    bert_db = bert_vectors.get()
    openai_db = bert_vectors.get()
    bert_db_size = len(bert_db["ids"])
    openai_db_size = len(openai_db["ids"])
    print("bert openai db sizes:", bert_db_size, openai_db_size)
    if bert_db_size == 0:
        print("filling vector DBs")
        init_dbs(bert_vectors, openai_vectors)
    else:
        for id, doc in zip(bert_db["ids"], bert_db["documents"]):
            id_to_doc[id] = doc
            print(id, doc)

    bert_top_docs = {}
    openai_top_docs = {}
    for query in queries:
        print("QUERY", query)
        bert_results = bert_vectors.similarity_search_with_score(query, 10)
        bert_top_doc_id = bert_results[0][0].id
        if not bert_top_doc_id in bert_top_docs:
            bert_top_docs[bert_top_doc_id] = 0
        bert_top_docs[bert_top_doc_id] += 1

        openai_results = openai_vectors.similarity_search_with_score(query, 1)
        openai_top_doc_id = openai_results[0][0].id
        if not openai_top_doc_id in openai_top_docs:
            openai_top_docs[openai_top_doc_id] = 0
        openai_top_docs[openai_top_doc_id] += 1
    print("TOP BERT")
    for key in bert_top_docs:
        keyname = key
        if key in doc_id_to_texas_code_section:
            keyname = doc_id_to_texas_code_section[key]
        text = ""
        if key in id_to_doc:
            text = id_to_doc[key]
        print(keyname, bert_top_docs[key], text)
    print()

    print("TOP OPENAI")
    for key in openai_top_docs:
        keyname = key
        if key in doc_id_to_texas_code_section:
            keyname = doc_id_to_texas_code_section[key]
        text = ""
        if key in id_to_doc:
            text = id_to_doc[key]
        print(keyname, openai_top_docs[key], text)

if __name__ == "__main__":
    main()
    print('exit')
