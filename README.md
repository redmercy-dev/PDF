
This project provides a utility for extracting content from PDF documents, processing the content, and then exporting the extracted information to Google Sheets. It uses various libraries including pytesseract for image-to-text conversion, pypdfium2 for PDF to image conversion, and googleapiclient for Google Sheets integration. Additionally, it incorporates the power of OpenAI's GPT model for extracting structured data from content.

Features

Convert PDF documents into images.
Extract text from these images.
Utilize OpenAI's GPT model to extract structured data from text content.
Upload and process multiple PDFs simultaneously.
Export extracted data to Google Sheets.
Streamlit based user interface for ease of use.
Setup
Requirements
Python 3.x
A Google Cloud Project with Sheets API enabled and OAuth 2.0 Client IDs configured.
OpenAI account for GPT model access.
Installation
Clone this repository:

bash
git clone <repository_link>
Navigate to the project directory and install required dependencies:


pip install pytesseract pypdfium2 streamlit google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client pandas
You must have Tesseract installed on your system. Follow installation instructions for your platform: Tesseract Installation Guide

Configuration
Obtain OpenAI API key from OpenAI.

Create a Google Cloud Project, enable Sheets API, and set up OAuth 2.0. Download the auth.json credentials file and place it in the root directory of this project. More details on setting up Google Sheets API can be found here.

(Optional) Change the sheet_id in the main() function to your Google Sheets ID.

Usage
Run the Streamlit app:

arduino

streamlit run <script_name>.py
The Streamlit interface should open in your default web browser.

Input your OpenAI API key.

Upload your PDF files.

View the extracted results and confirm their export to Google Sheets.

Note
Ensure you have proper permissions and quota limits set up in Google Cloud Console and OpenAI for seamless usage.

Contributions
Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

License
This project is MIT licensed.

