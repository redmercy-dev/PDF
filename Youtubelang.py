from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from pytesseract import image_to_string
from PIL import Image
from io import BytesIO
import pypdfium2 as pdfium
import streamlit as st
import multiprocessing
from tempfile import NamedTemporaryFile
import pandas as pd
import json
import pickle
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from google_auth_oauthlib.flow import InstalledAppFlow

import gspread
from google.oauth2 import service_account



# Authentication function for Google Sheets
def authenticate_google_sheets():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ],
    )
    client = gspread.authorize(credentials)
    return client

# Function to append DataFrame to Google Sheets
def append_to_sheet(data_frame, sheet_url):
    client = authenticate_google_sheets()
    sheet = client.open_by_url(sheet_url).sheet1
    sheet.clear()  # Clear the sheet before adding new data
    sheet.update([data_frame.columns.values.tolist()] + data_frame.values.tolist())



# 1. Convert PDF file into images via pypdfium2


def convert_pdf_to_images(file_path, scale=300/72):
    print(f"Converting PDF at {file_path}")

    pdf_file = pdfium.PdfDocument(file_path)

    page_indices = [i for i in range(len(pdf_file))]

    renderer = pdf_file.render(
        pdfium.PdfBitmap.to_pil,
        page_indices=page_indices,
        scale=scale,
    )

    final_images = []

    for i, image in zip(page_indices, renderer):

        image_byte_array = BytesIO()
        image.save(image_byte_array, format='jpeg', optimize=True)
        image_byte_array = image_byte_array.getvalue()
        final_images.append(dict({i: image_byte_array}))

    return final_images

# 2. Extract text from images via pytesseract


def extract_text_from_img(list_dict_final_images):

    image_list = [list(data.values())[0] for data in list_dict_final_images]
    image_content = []

    for index, image_bytes in enumerate(image_list):

        image = Image.open(BytesIO(image_bytes))
        raw_text = str(image_to_string(image))
        image_content.append(raw_text)

    return "\n".join(image_content)


def extract_content_from_url(url: str):
    images_list = convert_pdf_to_images(url)
    text_with_pytesseract = extract_text_from_img(images_list)

    return text_with_pytesseract


# 3. Extract structured info from text via LLM
def extract_structured_data(content: str, data_points, openai_key):
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613", openai_api_key=openai_key)
    template = """
    You are an expert admin people who will extract core information from documents

    {content}

    Above is the content; please try to extract all data points from the content above 
    and export in a JSON array format:
    {data_points}

    Now please extract details from the content  and export in a JSON array format, 
    return ONLY the JSON array:
    """

    prompt = PromptTemplate(
        input_variables=["content", "data_points"],
        template=template,
    )

    chain = LLMChain(llm=llm, prompt=prompt)

    results = chain.run(content=content, data_points=data_points)

    return results


def main():
    default_data_points = {
        "invoice_item": "What is the item that was charged?",
        "Amount": "How much does the invoice item cost in total?",
        "Company_name": "Which company issued the invoice?",
        "invoice_date": "When was the invoice issued?"
    }

    st.set_page_config(page_title="Doc extraction", page_icon=":bird:")

    st.header("Doc extraction :bird:")

    # Capture the OpenAI key from the user
    openai_key = st.text_input("Enter your OpenAI API key:", type="password")

    data_points = st.text_area(
        "Data points", value=json.dumps(default_data_points, indent=4), height=170)

    uploaded_files = st.file_uploader("Upload PDFs", accept_multiple_files=True)

    if uploaded_files and data_points:
        results = []

        for file in uploaded_files:
            with NamedTemporaryFile(dir='.', suffix='.pdf', delete=False) as f:
                f.write(file.getbuffer())
                content = extract_content_from_url(f.name)

                data = extract_structured_data(content, data_points, openai_key)
                json_data = json.loads(data)

                if isinstance(json_data, list):
                    results.extend(json_data)  # Use extend() for lists
                else:
                    results.append(json_data)  # Wrap the dict in a list

        if results:
            try:
                df = pd.DataFrame(results)
                st.subheader("Results")
                st.dataframe(df)  # Display the dataframe

                # Allow the user to save the results to Google Sheets
                if st.button("Save to Google Sheets"):
                    # Direct Google Sheets link
                    sheet_url = "https://docs.google.com/spreadsheets/d/1mpIZ2_4EzQ5-cAabEJifdjh5EgcGD_UH8PlJsQlxkMc/edit"
                    append_to_sheet(df, sheet_url)
                    st.success('Data has been written to Google Sheets')
            except Exception as e:
                st.error(f"An error occurred: {e}")


          


if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
