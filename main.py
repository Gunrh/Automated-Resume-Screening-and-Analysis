######### version with NLP + history_warehouse
import tkinter as tk
import os
import util
import json
from datetime import datetime
from tkinter import messagebox
from fpdf import FPDF
import re
from fuzzywuzzy import fuzz
from tkinter import filedialog
from PyPDF2 import PdfReader
import webbrowser

class App:
    def __init__(self, master):
        self.master = master
        self.path = tk.StringVar()
        self.read_files_label = None
        self.key_word_list = []
        self.threshold = tk.StringVar()
        self.flag_filtered = None
        self.hist_list = util.check_history_file()

        

        # #Gui color styles
        # color_btn = "#A0D8B3"
        # text_style = "Helvetica"
        # color_bg = "#F2F2F2"








     
        self.contact_button= tk.Button(master, text="Contact Us", font=(text_style,10, "bold"), bg="#FEA1A1", command=self.open_linkedin)
        self.contact_button.pack(anchor='w')

        self.user_language = tk.StringVar()
        self.user_language.set("English") 

        self.user_language_label =  tk.Label(master, text=f"Display language: {self.user_language.get()}", font=(text_style, 10, "bold"), bg=color_bg)
        self.user_language_label.pack(anchor ="nw")


        self.user_language_radbutton_he  = tk.Radiobutton(master, text="Hebrew",font=(text_style, 10), variable=self.user_language, value="Hebrew", bg=color_bg,command=self.GUI_language)
        self.user_language_radbutton_he.pack(anchor= 'w')

        self.user_language_radbutton_en  = tk.Radiobutton(master, text="English",font=(text_style, 10), variable=self.user_language, value="English", bg=color_bg,command=self.GUI_language)
        self.user_language_radbutton_en.pack(anchor= 'sw')


        

        self.label = tk.Label(master, text="Enter a Path Name:", font=(text_style, 12, "bold"), bg=color_bg)
        self.label.pack()

        self.entry = tk.Entry(master, textvariable=self.path)
        self.entry.pack()

        self.browse_button = tk.Button(master, text="Browse",font=(text_style,10),bg= color_btn,command=self.browse)
        self.browse_button.pack()

        self.label_lang = tk.Label(master, text="Choose which language you want to check the resumes", font=("TkDefaultFont", 12, "bold"), bg=color_bg)
        self.label_lang.pack()


        self.lang_selected = tk.StringVar()
        self.lang_selected.set("English Only")

        self.hebrew_only_button = tk.Radiobutton(master, text="Hebrew Only",font=(text_style, 10), variable=self.lang_selected, value="Hebrew Only", bg=color_bg)
        self.hebrew_only_button.pack(anchor='w')

        self.english_only_button = tk.Radiobutton(master, text="English Only",font=(text_style, 10), variable=self.lang_selected, value="English Only", bg=color_bg)
        self.english_only_button.pack(anchor='w')

        self.hebrew_and_english_button = tk.Radiobutton(master, text="Hebrew and English", font=(text_style, 10),variable=self.lang_selected, value="Hebrew and English", bg=color_bg)
        self.hebrew_and_english_button.pack(anchor='w')

        
        self.label_threshold = tk.Label(master, text="Enter minimum threshold of match you want in percentage (0-100):", font=(text_style, 12, "bold"), bg=color_bg)
        self.label_threshold.pack()

        self.threshold_entry = tk.Entry(master, textvariable=self.threshold)
        self.threshold_entry.pack()


        # #keywords labels
        self.add_key_label = tk.Label(master, text="Enter keywords to filter relevant files", font=(text_style, 12, "bold"), bg=color_bg)
        self.add_key_label.pack()

        self.add_key_entry = tk.Entry(master)
        self.add_key_entry.pack()

        self.add_key_button = tk.Button(master, text="Add key word", font=(text_style,10), bg=color_btn, command=self.add_key)
        self.add_key_button.pack()
        self.clean_all_button = tk.Button(master, text="Clean all keywords", font=(text_style,10), bg=color_btn, command=self.clean_all_keywords)
        self.clean_all_button.pack(pady=5)

        # Uploading a job requirements file for quick keyword filtering
        self.upload_keyword_pdf = tk.Button(master, text="Uploading a PDF job file for keyword filtering", font=(text_style, 9), bg=color_btn, command=self.upload_job_requirements_file)
        self.upload_keyword_pdf.pack(pady=5)

        



        self.key_frame = tk.Frame(master)
        self.key_frame.pack()

        self.display_keys()

        
     

        self.resu_filter_label = tk.Label(master, text="  ", font=(text_style, 12), bg=color_bg)
        self.resu_filter_label.pack()

        self.create_pdf_button = tk.Button(master, text="Create PDF file",font=(text_style),bg=color_btn, command=self.create_pdf)

        self.dashboard_button = tk.Button(master, text="open data dashboard",font=(text_style),bg=color_btn, command=self.open_website)
        
        self.filter_button = tk.Button(master, text="Start filtering resumes", command=self.submit, font=(text_style, 14),bg=color_btn)
        self.filter_button.pack(pady=25)



        


    def browse(self):
        self.path.set(filedialog.askopenfilename())
        # path_cv =format(self.path.get())
        folder_path =self.path.get()
        dir_path = os.path.dirname(folder_path)  # get the directory name from the path

        #read the pdf files from the dir_path
        pdf_names = util.create_pdf_name_list(dir_path)

        # change the color label to red if the folder dont container pdf files
        
        if len(pdf_names) == 0:
            self.label.config(text=f" Error - The Folder dont have pdf files to read", fg="red")
        else:
            self.label.config(text=f"You read from the folder  {len(pdf_names)} pdf files", fg="green")

        print(dir_path)


    def submit(self):

        ############# get the path for dir to import the json ###########
        folder_path = self.path.get()
        dir_path = os.path.dirname(folder_path)  # get the directory name from the path
        ### ------ my added code : to create json data of all CV
        print(f"the path: {dir_path}")


          ######### filter to specific language ########
        choosed_resume_lang=[]
        

        # # filter the PDF names based on the selected language
        if self.lang_selected.get() == "Hebrew Only":
            choosed_resume_lang.append( util.return_list_of_pdf_with_hebrew_content_only(dir_path))

        elif self.lang_selected.get() == "English Only":
            choosed_resume_lang.append( util.create_pdf_name_list(dir_path))

        elif self.lang_selected.get() == "Hebrew and English":
            choosed_resume_lang.append( util.create_pdf_name_list(dir_path))

            
        ######### filter to threshold percentage ########
        threshold_percentage = self.threshold.get()

        if not threshold_percentage.isdigit() or int(threshold_percentage) < 0 or int(threshold_percentage) > 100:
            self.label_threshold.config(text="Threshold percentage must be a number between 0 and 100.", fg="red")
            return

        self.label_threshold.config(text="Threshold percentage:", fg="black")
        
        threshold_percentage = int(threshold_percentage)

       


        #what folder name to put the json file
        folder_name = os.path.basename(dir_path)
        
      



        # create json file with matching_results of CV
        matching_results=[]



        for path_cv in choosed_resume_lang[0]:
            full_path = folder_name+'\\'+path_cv
            matching_results= util.get_datalist_cv(full_path,self.key_word_list,path_cv)

        util.get_jsonfile(matching_results)
        util.remove_duplicate_emails()

        with open('filtered_resumes.json', 'r') as f:
            filtered_resumes1 = json.load(f)

        filtered_resumes = util.filter_matching_results(filtered_resumes1 , threshold_percentage)


        file_name = 'filtered_resumes.json'
        with io.open(file_name, 'w+') as f:
            f.write(json.dumps(filtered_resumes, ensure_ascii=False))

        util.save_jsfile(filtered_resumes)
        self.flag_filtered=1

        pdf_names = util.create_pdf_name_list(dir_path)
        
        self.filtered_cv_size =len(filtered_resumes)
        self.total_pdf = len(pdf_names)

        if self.user_language.get() =="English":
            self.resu_filter_label.config(text=f"{len(filtered_resumes)} out of {len(pdf_names)} CVs that passed the filters ", fg="green")
        elif self.user_language.get() =="Hebrew":
            self.resu_filter_label.config(text=f"קורות חיים שעברו את המסננים {len(filtered_resumes)} מתוך {len(pdf_names)} ", fg="green")

        ########################
        
        # Update hist_list with grouped keyword counts
        for i, keyword in enumerate(self.key_word_list):
            for j, hist_entry in enumerate(self.hist_list):
                if keyword in hist_entry:
                    keyword_count = int(hist_entry.split(":")[1].strip()) + 1
                    self.hist_list[j] = f"{keyword}: {keyword_count}"
                    break
            else:
                self.hist_list.append(f"{keyword}: 1")

        # Save hist_list to "history_warehouse.txt" file
        with open("history_warehouse.txt", "w") as file:
            file.write("\n".join(self.hist_list))


        ########################

   
   


        self.create_pdf_button.pack(side=tk.LEFT, padx=(20,0), pady=20)
        self.dashboard_button.pack(side=tk.RIGHT, padx=(0,20), pady=20)





        



    def add_key(self):


        key = self.add_key_entry.get()
        key = key.lower()
        if key:
            if key in self.key_word_list:
                messagebox.showerror("Error", f"{key} already exists in the list")
            else:
                self.key_word_list.append(key)
                self.add_key_entry.delete(0, tk.END)
                self.display_keys()
                
    def add_key_file(self, filtered_keywords):
        
        for filtered_word in filtered_keywords:
            self.key_word_list.append(filtered_word)
            self.add_key_entry.delete(0, tk.END)
            self.display_keys()
        
    

    def remove_key(self, key):
        self.key_word_list.remove(key)
        self.display_keys()


    def display_keys(self):
        # clear the current frame
        for widget in self.key_frame.winfo_children():
            widget.destroy()

        # create a label and button for each key in the list_keys
        row_num = 0
        col_num = 0
        for key in self.key_word_list:
            if col_num == 5:
                col_num = 0
                row_num += 1
            key_frame = tk.Frame(self.key_frame)
            key_frame.grid(row=row_num, column=col_num, sticky="W")

            remove_button = tk.Button(key_frame, text="X", fg="red", command=lambda key=key: self.remove_key(key))
            remove_button.pack(side=tk.LEFT)

            key_label = tk.Label(key_frame, text=key)
            key_label.pack(side=tk.LEFT)

            col_num += 1



    def clean_all_keywords(self):
        self.key_word_list.clear()
        self.display_keys()

        

    def upload_job_requirements_file(self):
        """""function allows the HR user to upload a job requirements file in PDF format.
        and filters from requirements by use automation and NLP  the most relevant keywords  """



        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])

        if file_path:

            text = util.extract_keywords(file_path)

            filtered_keywords = [re.sub(r'[^a-zA-Z]', ' ', word) for word in text]  # Replace non-letters with space
            filtered_keywords = [word.strip() for word in " ".join(filtered_keywords).split()]  # Split and remove leading/trailing spaces
            filtered_keywords = [word.lower() for word in filtered_keywords]  # Convert to lowercase

            filtered_keywords = list(set(filtered_keywords))  # Remove duplicates
            filtered_keywords = [word for word in filtered_keywords if len(word) > 2]  # Remove words with 2 or fewer letters
            non_keywords_list =['advantage', 'mind', 'role', 'have', 'both','can'
                                'skills','skill' 'knowledge', 'work', 'problem',
                                'strong','for', 'user', 'and', 'such','must','with',
                                'requirements','year','making','make','detail','knowledge','minimum',
                                'experience','maximum','related','professional','english','field','spoken',
                                'the','more','availability','real','owning','these','fluent','following','from','time'
                                ,'education','deliver','peer','collaborative','similar','including','etc','environment','ability'
                                ,'review','distributed','development','easily','understand','working','deploying','integration','high','low',
                                'proven','languages','others','code','industry','what','are','using','use','looking','open','push','tools','very',
                                'player','drive','attitude','through','self','familiarity','techniques','part','plus','proficiency','equivalent']
            
            #remove words with simmalri high than 80% with values from non_keywords_list 
            filtered_keywords = [word for word in filtered_keywords if all(fuzz.ratio(word, non_keyword) < 80 for non_keyword in non_keywords_list)]

            #remove the values with similar   between the values too
            filtered_keywords = [word for i, word in enumerate(filtered_keywords) if all(fuzz.ratio(word, other_word) < 80 for other_word in filtered_keywords[i+1:])]

            
            # Uses NLP to filter out verbs, adjectives, and duplicate words
            filtered_keywords = util.filter_keywords(filtered_keywords, non_keywords_list)



        
            for key in filtered_keywords:
                if key in self.key_word_list:
                    messagebox.showerror("Error", f"{key} already exists in the list")
                else:
                    self.key_word_list.append(key)
                    self.add_key_entry.delete(0, tk.END)
                    self.display_keys()
            print(f"total added keywords with nlp:  {len(filtered_keywords)}")




                
    def create_pdf(self):
        util.remove_duplicate_emails()

        with open('filtered_resumes.json', 'r') as f:
            filtered_resumes = json.load(f)

        threshold_percentage = self.threshold.get()
        threshold_percentage = int(threshold_percentage)
        
        filtered_resumes = util.filter_matching_results(filtered_resumes , threshold_percentage)

        # sort resumes by percentage in descending order
        filtered_resumes.sort(key=lambda x: x['percentage'], reverse=True)
        print(f"the key list: {self.key_word_list}")

        #get the full path for CV folder
        folder_path = self.path.get()
        dir_path = os.path.dirname(folder_path)  # get the directory name from the path

        

        # Create PDF document
        pdf = FPDF()
        pdf.add_page()

        # Add title and date
        pdf.set_font("Arial", 'B', size=20)
        pdf.cell(200, 10, txt="Filtered Resumes ", ln=0, align='C')
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 10, txt=datetime.now().strftime("%d/%m/%Y"), ln=1, align='R')

        
        pdf.cell(0,5, txt=f"with the following filters:", ln=1, align='L')
        pdf.cell(0, 5, txt=f"Key words:",ln=1, align='L')
        pdf.set_font('Arial', '', 9)  # set regular font
        for i, keyword in enumerate(self.key_word_list, start=1):
            if i % 10 == 0:  # check if it's the 10th keyword
                pdf.cell(0, 5, keyword, ln=1)  # print keyword and move to the next line
            else:
                pdf.cell(20, 5, keyword)  # print keyword with 20 units width
        pdf.cell(0,5, txt= " ",ln=1, align='L')
        

        pdf.cell(0,5, txt=f"Threshold : {str(self.threshold.get())} ",ln=1, align='L')
        pdf.cell(0, 5, txt=f"Selected language: : {self.lang_selected.get()} ",ln=1, align='L')

        pdf.cell(200, 20, txt="", ln=2, align='L')

        for resume in filtered_resumes:

            pdf.set_font('Arial', 'B', 10) # set bold font
            pdf.cell(30, 5, 'File Name: ', 0) # print bold text
            pdf.set_font('Arial', '', 10) # set regular font
            pdf.cell(30, 5, resume['pdf_filename'], 0) # print regular text
            pdf.cell(0, 5,  ' ', ln=1)  # adds a new line after this line


            pdf.set_font('Arial', 'B', 9)  # set bold font
            pdf.cell(80, 5, 'Matching percentages according to filters: ', 0)  # print bold text
            pdf.set_font('Arial', '', 10)  # set regular font
            if resume['percentage'] == 100:
                pdf.set_text_color(0, 128, 0)  # set font color to green
            pdf.cell(30, 5, '{:.2f}%'.format(resume['percentage']), 0)  # print regular text with % symbol and 2 decimal places
            pdf.set_text_color(0, 0, 0)  # reset font color
            pdf.cell(0, 5, ' ', ln=1)  # adds a new line after this line


            pdf.set_font('Arial', 'B', 10) # set bold font
            pdf.cell(30, 5, 'Score: ', 0) # print bold text
            pdf.set_font('Arial', '', 10) # set regular font
            pdf.cell(30, 5,str( resume['score']), 0) # print regular text
            pdf.cell(0, 5,  ' ', ln=1)  # adds a new line after this line

            pdf.set_font('Arial', 'B', 10) # set bold font
            pdf.cell(30, 5, 'keywords: ', 0) # print bold text
            pdf.set_font('Arial', '', 10) # set regular font
            pdf.cell(30, 5, str(resume['matching_keywords']), 0) # print regular text
            pdf.cell(0, 5,  ' ', ln=1)  # adds a new line after this line

            pdf.set_font('Arial', 'B', 10) # set bold font
            pdf.cell(30, 5, 'Email: ', 0) # print bold text
            pdf.set_font('Arial', '', 10) # set regular font
            pdf.cell(30, 5, str(resume['email']), 0) # print regular text
            pdf.cell(0, 5,  ' ', ln=1)  # adds a new line after this line

            
            pdf.set_font('Arial', 'B', 10) # set bold font
            pdf.cell(30, 5, 'Link: ', 0) # print bold text
            pdf.set_font('Arial', 'U', 10) # set underline font
            path_file= f"{dir_path}\\{resume['pdf_filename']}"
            pdf.cell(0, 5, 'click to open file', ln=1, link=path_file) # print clickable link with text and URL
            pdf.set_font('Arial', '', 10) # set regular font

            pdf.cell(0, 5,  ' ', ln=1)  # adds a new line after this line
            pdf.cell(0, 5,  ' ', ln=1)  # adds a new line after this line
            pdf.cell(0, 5,  ' ', ln=1)  # adds a new line after this line

        # Save PDF
        pdf.output("filtered_Matched_resumes.pdf")


    def open_website(self):
        webbrowser.open("data_dashbored.html")
    def open_linkedin(self):
        webbrowser.open("https://www.linkedin.com/in/omri-dvash-bigdata/")
    
    def GUI_language(self):

        if self.user_language.get() =="English":

            self.contact_button.config(text="Contact Us")
            self.user_language_label.config( text=f"Display language: {self.user_language.get()}")
            # self.user_language_radbutton_he.config(text=self.user_language.get())

            self.browse_button.config(text="Browse")
            self.label_lang.config(text="Choose which language you want to check the resumes") # הוספת דגל

            self.hebrew_only_button.config(text="Hebrew Only")
            self.english_only_button.config(text="English Only")
            self.hebrew_and_english_button.config(text="English and Hebrew")

            self.label_threshold.config( text="Enter minimum threshold of match you want in percentage (0-100):")# הוספת דגל

            self.add_key_label.config(text="Enter keywords to filter relevant files")

            self.add_key_button.config(text="Add key word")


            self.clean_all_button.config( text="Clean all keywords") 
            self.upload_keyword_pdf.config( text="Uploading a PDF job file for keyword filtering") 

            
            self.create_pdf_button.config(text="Create PDF file")

            self.dashboard_button.config ( text="open data dashboard")

            if self.flag_filtered ==1:
              self.resu_filter_label.config(text=f"{ self.filtered_cv_size} out of {self.total_pdf} CVs that passed the filters ", fg="green")
              




        else:
            self.contact_button.config(text="יצירת קשר")
            self.user_language_label.config( text=f"{self.user_language.get()} : שפת תצוגה ")
            self.browse_button.config(text="בחירת תקייה")
            self.label_lang.config(text="בחר את השפה שבה תרצה לסנן את קבצי הקורות חיים") # הוספת דגל

            
            self.hebrew_only_button.config(text="עברית בלבד")
            self.english_only_button.config(text="אנגלית בלבד")
            self.hebrew_and_english_button.config(text="אנגלית ועברית")

            self.label_threshold.config( text="הזן את סף ההתאמה המינימלי שאתה רוצה באחוזים (0-100)") # הוספת דגל
            
            self.add_key_label.config(text="הזן מילות מפתח כדי לסנן קבצים רלוונטיים")

            self.add_key_button.config(text="הוסף מילת מפתח")

            
            self.clean_all_button.config( text="נקה את כל מילות המפתח") 
            self.upload_keyword_pdf.config( text="העלאת קובץ דרישות משרה \nPDF לסינון מילות מפתח") 

              
            self.create_pdf_button.config(text="צור קובץ PDF")
            self.dashboard_button.config ( text="לפתוח דאשבורד נתונים")

            if self.flag_filtered == 1:
                    self.resu_filter_label.config(text=f"קורות חיים שעברו את המסננים {self.filtered_cv_size} מתוך {self.total_pdf} ", fg="green")

            

import io

  

root = tk.Tk()

#Gui color styles
color_btn = "#A0D8B3"
text_style = "Helvetica"
# Helvetica
color_bg = "#F2F2F2"
root.configure(bg=color_bg)

app = App(root)


# add widgets to the root window here
root.mainloop()

        
