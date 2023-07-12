from pdfminer.high_level import extract_text

import os
import unicodedata
from typing import List, Tuple
import json
import fuzz
from tkinter import filedialog
from PyPDF2 import PdfReader
import re

import spacy



#### NLP for english tokens
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

nlp = spacy.load("en_core_web_sm")
def filter_keywords(keywords, link_words):
    """""Using NLP, identify tokens that are Verbs,ADJ,ADV 
      They are usually not keywords"""
    filtered_keywords = []

    doc = nlp(" ".join(keywords))
    for token in doc:
        if token.pos_ not in ["VERB", "ADJ", "ADV"] and token.text not in link_words:

            filtered_keywords.append(token.text)

    return filtered_keywords
#############################################################################
##### NLP for hebrew tokens
# nlp = spacy.load("he_core_news_sm")

# def filter_keywords(keywords, link_words):
#     filtered_keywords = []

#     doc = nlp(" ".join(keywords))
#     for token in doc:
#         if (
#             token.pos_ != "VERB"
#             and token.text not in link_words
#             and token.pos_ != "ADJ"
#             and token.pos_ != "ADV"
#             and token.pos_ != "NOUN"
#         ):
#             filtered_keywords.append(token.text)

#     return filtered_keywords

def extract_keywords(file_path):
    keywords = []

    with open(file_path, 'rb') as file:
        pdf_reader = PdfReader(file)

        for page in pdf_reader.pages:
            keywords += page.extract_text().split()

        return keywords




def get_email( text):
    words = text.split()
    for word in words:
        if "@" in word and "." in word:
            return word
    return "No email"



# def get_phone_number(text):
#     phone_pattern = r"\d{10}|\d{3}-\d{7}"  # Patterns for 10-digit number or 3-digit + '-' + 7-digit number
#     match = re.search(phone_pattern, text)
#     if match:
#         return match.group()
#     else:
#         return "No phone number"


def get_phone_number(text):
    patterns = [
        r"\+972\s?(\d{9})",           # +972 followed by 9 digits
        r"\+972\s?(\d{3}-\d{7})",     # +972 followed by 3 digits, hyphen, and 7 digits
        r"(\d{4}-\d{6})",             # 4 digits, hyphen, and 6 digits
        r"(\d{3}-\d{7})",             # 3 digits, hyphen, and 7 digits
        r"(\d{3}-\d{3}-\d{4})",       # 3 digits, hyphen, 3 digits, and 4 digits
        r"(\d{10})"                   # 10 digits
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            phone_number = match.group(1)
            phone_number = phone_number.replace("-", "").replace("+972", "0")
            return phone_number

    return "No phone number"


def get_resume_fullname(input_pdf_file_name):
    # Remove .pdf suffix
    text = re.sub(r'\.pdf$', '', input_pdf_file_name)

    # Remove numbers
    text = re.sub(r'\d', '', text)

    # Remove "."
    text = re.sub(r'\.', '', text)

    # Remove "-"
    text = re.sub(r'-', '', text)

    # Remove "CV"
    text = re.sub(r'CV', '', text, flags=re.IGNORECASE)

    # Remove "resume"
    text = re.sub(r'resume', '', text, flags=re.IGNORECASE)

    # Remove extra whitespaces
    text = ' '.join(text.split())

    return text


def find_linkedin_url(text):
    # Regular expression pattern to match LinkedIn URLs
    pattern = r"(https?://(?:www\.)?linkedin\.com/(?:[a-zA-Z]{2}/)?[a-zA-Z0-9-]+)"

    # Find all matches in the text
    matches = re.findall(pattern, text)

    # Check if any match is a valid LinkedIn URL
    for match in matches:
        if "linkedin.com/in/" in match:
            return match

    return None

def create_pdf_name_list( _path): #pdf names can be english \hebrew
    """""The function input path of folders with pdf files and
      return clean list with all pdf file names"""
    folder_path = _path
    pdf_list =[] #to save the path for pdf in hebrew too


    # Get a list of all files in the folder
    with os.scandir(folder_path) as entries:
        # Loop over the entries and print the names of the PDF files
        for entry in entries:
            # Check if the entry is a file and has a PDF extension
            if entry.is_file() and entry.name.endswith('.pdf'):
                # Get the file name encoded in the file system's default encoding
                file_name = entry.name.encode().decode('utf-8')
                pdf_list.append(file_name)

    # clean_pdf_names_list = [name.replace('\u200e', '').replace('\u200f', '') for name in pdf_list]

    return pdf_list #, clean_pdf_names_list


from pdfminer.high_level import extract_text
def return_list_of_pdf_with_hebrew_content_only(path):
    """""הפונקציה הזאת מקבלת ניתוב לתקייה עם קבצי פי-די-אף
    ומחזירה רשימה של כל הקבצי פי-די-אף שרשום בהם בשפה העברית
    """
    
    # Set the path to the folder containing PDF files
    # path = 'CV'
    folder_path = path

    # Create a list to store the paths of PDF files that contain Hebrew text
    pdf_hebrew_list = []

    # Get a list of all files in the folder
    with os.scandir(folder_path) as entries:
        # Loop over the entries and process the PDF files
        for entry in entries:
            # Check if the entry is a file and has a PDF extension
            if entry.is_file() and entry.name.endswith('.pdf'):
                # Get the file name encoded in the file system's default encoding
                file_name = entry.name.encode().decode('utf-8')
                # Create the full path to the PDF file
                pdf_file_path = os.path.join(folder_path, file_name)
                # Open the PDF file in read-binary mode
                with open(pdf_file_path, 'rb') as f:
                    # Extract the text from the PDF file
                    text = extract_text(f)
                    # Check if the extracted text contains any Hebrew characters
                    if any('HEBREW' in unicodedata.name(c) for c in text if c.isprintable()):
                        # If the text contains Hebrew characters, add the file path to the Hebrew list
                        pdf_hebrew_list.append(file_name)

    # Return the list of PDF file paths containing Hebrew text
    return pdf_hebrew_list 


def count_key_words(text,key_words): #return and dict with counts per every key words
    dict_count={}
    for word in key_words:

        count = text.lower().count(word)
        dict_count[word]= count
    return dict_count

matching_results=[]


# def get_datalist_cv(pdf_file_path, keyword_list: List[str],pdf_name) :
def get_datalist_cv(text, keyword_list: List[str],pdf_name) :


    """""פונקציה שמקבלת מערך של מילות מפתח ואת הנתיב למקום של הקורות חיים
    וממירה את הנתונים לקובץ גייסון עם המילות מפתח שנמצאו בקורות חיים,
    וכמה אחוז מהמילות המפתח נמצאו בקורות חיים מתוך סך כל מילות המפתח שהוגדרו"""


    # # Open the PDF file in read-binary mode

    # # print(pdf_file_path)

    # # matching_results=[]

    # with open(pdf_file_path, 'rb') as f:
    #     # Extract the text from the PDF file
    #     text = extract_text(f)

    # # Convert the text to lowercase to make matching case-insensitive
    # text = text.lower()

    # Initialize a list to store the matching keywords
    matching_keywords = []


    # Loop over the keywords and check if each one appears in the text
    for keyword in keyword_list:

        if keyword.lower() in text:
            matching_keywords.append(keyword)


    # Calculate the percentage of keywords that matched
    percentage = len(matching_keywords) / len(keyword_list) * 100
    
    #Calculate counts per every key word
    dict_count_keywords = count_key_words(text,matching_keywords)

    total_count = sum(dict_count_keywords.values())

    email = get_email(text)

    phone = get_phone_number(text)

    fullname=get_resume_fullname(pdf_name)
    # linkedin_profile = find_linkedin_url(text)



    matching_results.append({
            "pdf_filename": pdf_name,
            "fullname": fullname,
            "score": total_count,
            # "linkedin":linkedin_profile,
            "email":email,
            "phone" : phone,
            "matching_keywords": matching_keywords,
            "count_key_words": dict_count_keywords,
            "percentage": percentage
        })
    
   
    # Return the list of matching keywords and the percentage
    return matching_results

# Filters from the list of resumes according to a percentage match threshold
def filter_matching_results(matching_results, threshold):
    filtered_results = []
    for result in matching_results:
        if result['percentage'] >= threshold:
            filtered_results.append(result)

    return filtered_results

import io
import json

def get_jsonfile(data):
    json_file_name = 'All_Resumes_Data.json'
    with io.open(json_file_name, 'w+') as f:
        f.write(json.dumps(data, ensure_ascii=False))



def filter_CV_json_by_threshold(json_file_path,threshold_percentage):

    json_file_path = 'filtered_resumes.json'

    with open(json_file_path, 'r') as f:
        data = json.load(f)
    
    filtered_data = [d for d in data if d['percentage'] >= threshold_percentage]
    
    return filtered_data


def remove_duplicate_emails():
    with open('All_Resumes_Data.json', 'r') as f:
        filtered_resumes = json.load(f)

    email_dict = {}
    for resume in filtered_resumes:
        email = resume['email']
        if email not in email_dict:
            email_dict[email] = resume
        else:
            # If the email is already in the dictionary, replace the existing resume with the new one
            email_dict[email] = resume

    # Convert the dictionary back to a list
    filtered_resumes = list(email_dict.values())

    # Write the filtered resumes back to the file
    with open('filtered_resumes.json', 'w') as f:
        json.dump(filtered_resumes, f, indent=4)

    print('Duplicate emails removed.')




def save_jsfile(data):
    js_file_name = 'All_Resumes_Data.js'
    with io.open(js_file_name, 'w+', encoding='utf8') as f:
        f.write('const resumeData = ')
        json.dump(data, f, ensure_ascii=False)
        f.write(';')

        
#############

def check_history_file():
    file_path = "history_warehouse.txt"

    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            data = file.read()
            if data:
                history_list = data.split("\n")
            else:
                history_list = []
    else:
        history_list = []

    return history_list

