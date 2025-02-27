import time
import requests
from document_payload import DocumentPayload
import html2text

import os
from openai import OpenAI
from prompts import outerSystemPrompt, bridgeOnePrompt, bridgeTwoPrompt, chapterExtractionPrompt

def extract_summary(text):
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),  # This is the default and can be omitted
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system", "content": """
                    you are a system designed to help humans query legal data.
                    you will receive text of state law containing many sections.
                    sections have a number and a title formatted like this Sec. 301.001.  PURPOSE;  AGENCY GOALS;  DEFINITIONS.

                    focus on extracting information like this for each section

                    •	Confidentiality Terms: {private, classified, restricted, secure, sensitive}
                    •	Entities: {employer, government agency, third party, authorized recipient}
                    •	Authority Descriptors: {may disclose, is authorized to share, has the legal right to disclose}
                    •	Process Terms: {disclose, release, transmit, share, provide access}
                    •	Data Types: {records, forms, hearings, written documents, reports}
                    •	Parties: {employee, contractor, agency, public entity}
                    •	Purpose Descriptors: {required by law, permitted under rule, regulated by statute}

                    return a JSON object where keys are section number and names and values are extracted information
                    
                    do not skip any section
                """
            },
            { "role": "user", "content": f"chapter of the Texas state labor code: {text}" }
        ],
        model="gpt-4o",
    )
    summary_text = chat_completion.choices[0].message.content
    return summary_text

def main():
    # add a fake URL params to identify extracted summaries
    # we can use this to identify whether a vector match is raw text or a summary later
    # if we were more proper we would save this in document metadata
    url = "https://statutes.capitol.texas.gov/Docs/LA/htm/LA.301.htm"
    url += "?isSummaryV3"

    print("GET", url)
    response = requests.get(url)
    text = html2text.html2text(response.text)
    print("LLM thinking...")
    summary = extract_summary(text)
    print("SUMMARY", summary)

if __name__ == "__main__":
    main()
    print('exit')
