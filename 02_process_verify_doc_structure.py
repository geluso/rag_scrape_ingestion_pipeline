import json
import time
import psycopg2
import requests

from bs4 import BeautifulSoup
from document_payload import DocumentPayload
from typing import List, Tuple
import html2text


from db import create_default_connection, get_url_200_count, get_urls_count, \
    get_one_url_to_process, insert_zip_zip_distance, count_zip_zip_distance, get_url_processed_count, \
    update_url_success, get_all_urls
from smc_mapbox import MapBoxResponse

TOKEN_LIMIT = 350
BASE_URL = "https://4cb3-2601-602-8b82-92b0-64d0-4b7b-a51a-85fb.ngrok-free.app/"
BASE_URL = "http://localhost:8080/"

class TexasCode:
    def __init__(self, url):
        self.url = url
        self.code = None
        self.title = None
        self.subtitle = None
        self.chapter = None
        self.chapter_number = None
        self.subchapter = None
        self.sections = []

    def is_valid(self):
        if None in [self.code, self.title, self.subtitle, self.chapter, self.chapter_number, self.subchapter]:
            return False
        elif len(self.sections) == 0:
            return False
        else:
            for section in self.sections:
                section_title = self.get_section_title(section)
                if not section_title.startswith("Sec."):
                    return False
            return True

    def explain_invalidity(self):
        if self.code is None:
            print("Missing code")
        if self.title is None:
            print("Missing title")
        if self.subtitle is None:
            print("Missing subtitle")
        if self.chapter is None:
            print("Missing chapter")
        if self.chapter_number is None:
            print("Missing chapter_number")
        if self.subchapter is None:
            print("Missing subchapter")

    def get_section_title(self, section):
        if len(section) < 1:
            return ""
        first_line = section[0]
        first_line_split = first_line.split("  ")

        if len(first_line_split) >= 2:
            title = first_line_split[0] + " " + first_line_split[1]
            return title
        if len(first_line_split) == 0:
            return first_line_split[0]
        return first_line

    def __str__(self):
        jj = {
            "is_valid": self.is_valid(),
            "sections": len(self.sections),
            "code": self.code,
            "title": self.title,
            "subtitle": self.subtitle,
            "chapter": self.chapter,
            "chapter_number": self.chapter_number,
            "subchapter": self.subchapter
        }
        return json.dumps(jj)

    def check_header(self, soup):
        all_p = soup.find_all('p')

        text0 = all_p[0].get_text()
        text1 = all_p[1].get_text()
        text2 = all_p[2].get_text()
        text3 = all_p[3].get_text()
        text4 = all_p[4].get_text()
        text5 = all_p[5].get_text()

        if text0.endswith("CODE"):
            self.code = text0

        if text1.startswith("TITLE"):
            self.title = text1

        if text2.startswith("SUBTITLE"):
            self.subtitle = text2

        if text3.startswith("CHAPTER"):
            self.chapter = text3
            self.chapter_number = text3.split(" ")[1]

        if text4.startswith("SUBCHAPTER"):
            self.subchapter = text4

        # hack to account for an extra empty paragraph *puke*
        if text5.startswith("SUBCHAPTER"):
            self.subchapter = text5

    def get_start_section_paragraph_index(self):
        # Always return '5' for now, but perhaps do something more clever in the future.
        return 6

    def gather_sections(self, soup):
        section_start_index = self.get_start_section_paragraph_index()
        all_p = soup.find_all('p')[section_start_index:]
        section_prefix = f"Sec. {self.chapter_number}"

        section_paragraphs = []
        for one_p in all_p:
            text = one_p.get_text()
            if text.startswith(section_prefix):
                if len(section_paragraphs) > 0:
                    self.sections.append(section_paragraphs)
                section_paragraphs = [text]
            else:
                if len(text) > 0:
                    section_paragraphs.append(text)
        if len(section_paragraphs) > 0:
            self.sections.append(section_paragraphs)

    def section_to_chunk(self, section):
        words = []
        for paragraph in section:
            for word in paragraph.split(" "):
                words.append(word)
        chunks = []
        while len(words) > 0:
            chunk = " ".join(words[:TOKEN_LIMIT])
            words = words[TOKEN_LIMIT:]
            chunks.append(chunk)
        return chunks

    def code_to_section_chunks(self):
        section_chunks = []
        for section in self.sections:
            section_chunks.append(self.section_to_chunk(section))
        return section_chunks


def count_chunks(all_valid_codes):
    for one_valid_code in all_valid_codes:
        for section in one_valid_code.sections:
            total_words = 0
            for paragraph in section:
                words = paragraph.split(" ")
                total_words += len(words)
            chunks = total_words / TOKEN_LIMIT
            if chunks > 2:
                print(chunks, section[0], one_valid_code.url)
                print()

def fetch_or_create_metadata(parent_id, datatype, label, summary):
    response = requests.get(f'{BASE_URL}/metadata/?label={label}')
    jj = response.json()
    if "id" in jj:
        metadata_id = jj["id"]
        print("metadata GOT id:", metadata_id, label)
        return metadata_id
    response = requests.post(BASE_URL + '/metadata/', json={"parentId": parent_id, "datatype": datatype, "label": label})
    metadata_id = response.json()["id"]
    print("metadata GOT id:", metadata_id, label)
    return metadata_id

def create_chunk(parent_id, source, text):
    response = requests.post(BASE_URL + '/chunks/', json={"text": text, "source": source, "parentId": parent_id})
    print("created chunk", response.json()["id"])

def upload_valid_codes(codes):
    print("getting root")
    root_id = fetch_or_create_metadata(-1, "root", "Texas Statutes", "")
    print("got root")
    print("codes", len(codes))
    skip = 77
    count = 0
    for code in codes:
        if count < skip:
            print("SKIPPING COUNT:", count)
            count += 1
            continue
        print("PROCESSING COUNT:", count)
        count += 1

        # fetch or create code/title/subtitle/chapter/subchapter metadata
        code_id = fetch_or_create_metadata(root_id, "code", code.code, "")
        title_id = fetch_or_create_metadata(code_id, "title", code.title, "")
        subtitle_id = fetch_or_create_metadata(title_id, "subtitle", code.subtitle, "")
        chapter_id = fetch_or_create_metadata(subtitle_id, "chapter", code.chapter, "")
        subchapter_id = fetch_or_create_metadata(chapter_id, "subchapter", code.subchapter, "")

        for section in code.code_to_section_chunks():
            section_title = code.get_section_title(section)
            print("section title:", section_title)
            section_id = fetch_or_create_metadata(subchapter_id, "section", section_title, "")
            for chunk in section:
                create_chunk(section_id, code.url, chunk)
        
def main():
    conn = create_default_connection()
    fetched = get_url_200_count(conn)
    processed = get_url_processed_count(conn)
    total = get_urls_count(conn)
    print(f"{fetched} fetched")
    print(f"{processed} processed")
    print(f"{total} total URLs")

    all_valid_codes = []
    all_invalid_codes = []
    for row in get_all_urls(conn):
        if row is None:
            continue
        metadata, url, response = row

        soup = BeautifulSoup(response, 'html.parser')
        texas_code = TexasCode(url)
        texas_code.check_header(soup)
        texas_code.gather_sections(soup)
        if texas_code.is_valid():
            all_valid_codes.append(texas_code)
        else:
            all_invalid_codes.append(texas_code)
            print(url)
            texas_code.explain_invalidity()
            all_invalid_codes.append(texas_code)
    print("valid:", len(all_valid_codes))
    print("invalid:", len(all_invalid_codes))
    input("[press enter to continue]")

    # for one_valid_code in all_valid_codes:
    #     for index, section_chunks in enumerate(one_valid_code.code_to_section_chunks()):
    #         print(index, len(section_chunks), section_chunks)

    upload_valid_codes(all_valid_codes)


if __name__ == "__main__":
    main()
    print('exit')