
import tkinter as tk
import os
import util
import json
from datetime import datetime

import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from fpdf import FPDF
import tkinter as tk
import os
import util
import json
from datetime import datetime


import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from fpdf import FPDF
import os
 
class App:
    def __init__(self, master):
        self.master = master
        self.path = tk.StringVar()
        self.read_files_label = None
        self.lang_temp = None
        self.key_word_list = []
        self.threshold = tk.StringVar()






        self.label = tk.Label(master, text="Enter a Path Name:", font=("TkDefaultFont", 12, "bold"), bg="light blue")
        self.label.pack()

        self.entry = tk.Entry(master, textvariable=self.path)
        self.entry.pack()

        self.browse_button = tk.Button(master, text="Browse", command=self.browse)
        self.browse_button.pack()

        self.label_lang = tk.Label(master, text="Choose which language you want to check the resumes", font=("TkDefaultFont", 12, "bold"), bg="light blue")
        self.label_lang.pack()


        self.lang_selected = tk.StringVar()
        self.lang_selected.set("Hebrew Only")

        self.hebrew_only_button = tk.Radiobutton(master, text="Hebrew Only", variable=self.lang_selected, value="Hebrew Only", bg="light blue")
        self.hebrew_only_button.pack(anchor='w')

        self.english_only_button = tk.Radiobutton(master, text="English Only", variable=self.lang_selected, value="English Only", bg="light blue")
        self.english_only_button.pack(anchor='w')

        self.hebrew_and_english_button = tk.Radiobutton(master, text="Hebrew and English", variable=self.lang_selected, value="Hebrew and English", bg="light blue")
        self.hebrew_and_english_button.pack(anchor='w')

        
        self.label_threshold = tk.Label(master, text="Enter minimum threshold of match you want in percentage (0-100):", font=("TkDefaultFont", 12, "bold"), bg="light blue")
        self.label_threshold.pack()

        self.threshold_entry = tk.Entry(master, textvariable=self.threshold)
        self.threshold_entry.pack()


        
        self.add_key_label = tk.Label(master, text="Enter keywords to filter relevant files", font=("TkDefaultFont", 12, "bold"), bg="light blue")
        self.add_key_label.pack()


        self.add_key_entry = tk.Entry(master)
        self.add_key_entry.pack()

        self.add_key_button = tk.Button(master, text="Add key word", command=self.add_key)
        self.add_key_button.pack()

        self.key_frame = tk.Frame(master)
        self.key_frame.pack()

        self.display_keys()

        
     
        # self.filter_button = tk.Button(master, text="Start filtering resumes", command=self.submit)
        # self.filter_button.pack()

        self.resu_filter_label = tk.Label(master, text="  ", font=("TkDefaultFont", 12), bg="light blue")
        self.resu_filter_label.pack()

        self.create_pdf_button = tk.Button(master, text="Create PDF file", command=self.create_pdf)

        self.dashboard_button = tk.Button(master, text="open data dashboard")#, command=self.open_pdf_file)
        self.filter_button = tk.Button(master, text="Start filtering resumes", command=self.submit, font=("bold", 14), bg="red")
        self.filter_button.pack()



        


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
            self.lang_temp = "Hebrew Only"

        elif self.lang_selected.get() == "English Only":
            choosed_resume_lang.append( util.create_pdf_name_list(dir_path))
            self.lang_temp = "English Only"

        elif self.lang_selected.get() == "Hebrew and English":
            choosed_resume_lang.append( util.create_pdf_name_list(dir_path))
            self.lang_temp = "Hebrew and English"

            
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
        print(f"the len of filter resumes its {len(filtered_resumes)}")
        pdf_names = util.create_pdf_name_list(dir_path)
        self.resu_filter_label.config(text=f"{len(filtered_resumes)} out of {len(pdf_names)} CVs that passed the filters ", fg="green")


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

            key_label = tk.Label(key_frame, text=key)
            key_label.pack(side=tk.LEFT)

            remove_button = tk.Button(key_frame, text="X", fg="red", command=lambda key=key: self.remove_key(key))
            remove_button.pack(side=tk.LEFT)

            col_num += 1
        

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
        pdf.cell(0, 5, txt=f"Key words: {self.key_word_list} ",ln=1, align='L')
        pdf.cell(0,5, txt=f"Threshold : {str(self.threshold.get())} ",ln=1, align='L')
        pdf.cell(0, 5, txt=f"Selected language: : {self.lang_temp} ",ln=1, align='L')

        pdf.cell(200, 20, txt="", ln=2, align='L')

        for resume in filtered_resumes:

            pdf.set_font('Arial', 'B', 10) # set bold font
            pdf.cell(30, 5, 'File Name: ', 0) # print bold text
            pdf.set_font('Arial', '', 10) # set regular font
            pdf.cell(30, 5, resume['pdf_filename'], 0) # print regular text
            pdf.cell(0, 5,  ' ', ln=1)  # adds a new line after this line

            pdf.set_font('Arial', 'B', 9) # set bold font
            pdf.cell(80, 5, 'Matching percentages according to filters: ', 0) # print bold text
            pdf.set_font('Arial', '', 10) # set regular font
            if resume['percentage'] == 100:
                pdf.set_text_color(0, 128, 0) # set font color to green
            pdf.cell(30, 5, str(resume['percentage']) + "%", 0) # print regular text with % symbol
            pdf.set_text_color(0, 0, 0) # reset font color
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

     

  

root = tk.Tk()
root.configure(bg="light blue")

app = App(root)
root.mainloop()


# add widgets to the root window here
root.mainloop()
