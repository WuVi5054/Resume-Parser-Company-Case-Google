#Importing Libraries
import streamlit as st
import pymongo
from pymongo import MongoClient
from gridfs import GridFS
import pandas as pd
import numpy as np
import docx2txt
import pdfplumber
import certifi

#Setting the configs for the web page
st.set_page_config(page_title="Upload files to MongoDB Atlas", page_icon=":guardsman:", layout="wide")
#Getting the certificate to connect to the MongoDB database
ca = certifi.where()

# Connect to MongoDB Atlas
#In the <username>, <password>, <clustername> - Put your own credentials, remove the angle brackets too
client = pymongo.MongoClient(
"mongodb+srv://<username>:<password>@<clustername>.oyyvct8.mongodb.net/?retryWrites=true&w=majority", tlsCAFile=ca)


#Getting the data from the database
def get_data():
    db = client.uploads #establish connection to the 'uploads' database
    items = db.fs.files.find() # return all result from the 'fs.files' collection
    items = list(items)
    return items


# #Get an existing database
db = client.uploads

#Getting the database connection
fs = GridFS(db)

def save_file_to_db(file):
    # Save the file to GridFS
    file_id = fs.put(file, filename=file.name)
    return file_id

#Main function
def main():
    # st.set_page_config(page_title="Upload files to MongoDB Atlas", page_icon=":guardsman:", layout="wide")
    st.title("Upload files to MongoDB Atlas")
    #File uploader
    file = st.file_uploader("Choose a file", type=["docx", "txt", "pdf"])
    #Checking if file was choosen
    if file:
        #Checks if file is a .txt and outputs its contents
        if file.type == "text/plain":
            raw_text = str(file.read(), "utf-8")
            st.text(raw_text)
        #Checks if file is a .pdf and outputs its contents
        elif file.type == "application/pdf":
            try:
                with pdfplumber.open(file) as pdf:
                    pages = pdf.pages[0]
                    st.text(pages.extract_text())
            except:
                st.text("None")
        #Checks if file is a .docx and outputs its contents
        else:
            raw_text = docx2txt.process(file)
            st.text(raw_text)
        #Then saves the files to the database
        file_id = save_file_to_db(file)
        st.success("File was saved to the database with id: {}".format(file_id))

    data = get_data()

    for item in data:
        st.text(f"Filename: {item['filename']} \n Date uploaded: {item['uploadDate']}")
if __name__ == "__main__":
    main()