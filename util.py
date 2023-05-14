from pdfminer.high_level import extract_text

import os
import unicodedata
from typing import List, Tuple
import json


def get_email( text):
    words = text.split()
    for word in words:
        if "@" in word and "." in word:
            return word
    return "No email"





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


def get_datalist_cv(pdf_file_path, keyword_list: List[str],pdf_name) :


    """""פונקציה שמקבלת מערך של מילות מפתח ואת הנתיב למקום של הקורות חיים
    וממירה את הנתונים לקובץ גייסון עם המילות מפתח שנמצאו בקורות חיים,
    וכמה אחוז מהמילות המפתח נמצאו בקורות חיים מתוך סך כל מילות המפתח שהוגדרו"""


    # Open the PDF file in read-binary mode

    # print(pdf_file_path)

    # matching_results=[]

    with open(pdf_file_path, 'rb') as f:
        # Extract the text from the PDF file
        text = extract_text(f)

    # Convert the text to lowercase to make matching case-insensitive
    text = text.lower()

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

    email = get_email(text)


    matching_results.append({
            "pdf_filename": pdf_name,
            # "text": text,
            "email":email,
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

