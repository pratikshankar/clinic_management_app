import streamlit as st
import argparse
import os
import numpy as np
import streamlit as st
import pandas as pd
from datetime import datetime
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import sqlite3
from dotenv import load_dotenv
from utils import check_number,create_table,read_patient_data,save_patient_data
import os
import re
import time

load_dotenv()

db_path = os.getenv('db_path')
create_table(db_path)
# Add a title to your app

if 'patient_name' not in st.session_state:
    st.session_state['patient_name'] = ''
if 'patient_address' not in st.session_state:
    st.session_state['patient_address'] = ''
if 'total_sessions' not in st.session_state:
    st.session_state['total_sessions'] = ''  # Default value for number input
if 'amount_paid' not in st.session_state:
    st.session_state['amount_paid'] = ''
if 'source' not in st.session_state:
    st.session_state['source'] = ''
if 'mobile_number' not in st.session_state:
    st.session_state['mobile_number'] = 0
if 'physio_name' not in st.session_state:
    st.session_state['physio_name'] = ''



source_options=['google','walk_in','referral','website','social-media','others']
physio_list=['Dr.Swati Kumari(P.T)','Dr.Megha Gupta(P.T)','Dr.Devi (P.T)']
st.title("Patient Registration Portal")

# Input field for mobile number
st.session_state.mobile_number = st.text_input("Enter Patient's mobile number:",key="mobile_number_key")
valid_number,response=check_number(st.session_state.mobile_number)
st.write(response)
query='Select * from Patients where patient_mob_number=?'
params=st.session_state.mobile_number
exists=0
patients_data=read_patient_data(db_path,query,params)



if st.button("Check Number!") and  not patients_data.empty :
    exists=1
    st.write("Number already registered !",patients_data)
    patients_data=None
    st.session_state.mobile_number=0
if valid_number and exists != 1:
    st.session_state.patient_name=st.text_input("Enter Patient's Name:",key='patient_name_key',value=st.session_state.get('patient_name', ''))
    st.session_state.patient_mob_number=st.session_state.mobile_number
    st.session_state.patient_address=st.text_input("Enter Patient's Address:",key='patient_address_key',value=st.session_state.get('patient_address', ''))
    st.session_state.total_sessions = st.text_input("Total Sessions Signed Up For",key='total_sessions_key',value=st.session_state.get('total_sessions', ''))
    visits_completed=0
    visits_left=st.session_state.total_sessions
    st.session_state.amount_paid=st.text_input("Enter amount Paid:",key='amount_paid_key',value=st.session_state.get('amount_paid', '0'))
    st.session_state.source=st.session_state.source = st.selectbox(
    "How did patient know about the clinic?",  # Label
    source_options,  # Options
    index=source_options.index(st.session_state.get('source', source_options[0])) if st.session_state.get('source') else 0,  # Default selection
    key='source_key'  # Unique key
)#st.text_input("How did patient know about the clinic?",key='source_key',value=st.session_state.get('source', ''))
    st.session_state.physio_name = st.selectbox(
        "Consulting Physio Name:",  # Label
        physio_list,  # Options
        index=physio_list.index(st.session_state.get('physio_name', source_options[0])) if st.session_state.get(
            'physio_name') else 0,  # Default selection
        key='physio_name_key'  # Unique key
    )  # st.text_input("How did patient know about the clinic?",key='source_key',value=st.session_state.get('source', ''))
    print("till here")
    if st.button("Add Patient"):
        print("add button clicked")
        try:

            if st.session_state.patient_name and st.session_state.patient_mob_number.isdigit() and st.session_state.patient_address and st.session_state.total_sessions.replace('.', '',
                                                                                              1).isdigit()  and st.session_state.amount_paid.replace('.', '',
                                                                                              1).isdigit() :

                print("query building")
                query="INSERT INTO Patients (patient_name, patient_mob_number,patient_address, total_sessions, sessions_completed, sessions_left, amount_paid,source,physio_name) VALUES (?, ?, ?, ?, ?, ?,?,?,?)"
                params=(st.session_state.patient_name, st.session_state.patient_mob_number,st.session_state.patient_address, int(st.session_state.total_sessions), 0, int(st.session_state.total_sessions), float(st.session_state.amount_paid),st.session_state.source,st.session_state.physio_name,)
                ret_value=save_patient_data(db_path,query,params)
                if ret_value:

                    print("data saved")
                    # query = 'Select * from Patients where patient_mob_number=?'
                    # params = patient_mob_number
                    # patients_data = read_patient_data(db_path, query,params)
                    # st.write(patients_data)


                    st.session_state['patient_name'] = ''
                    st.session_state['patient_address'] = ''
                    st.session_state['total_sessions'] = ''  # Default value for number input
                    st.session_state['amount_paid'] = ''
                    st.session_state['source'] = ''
                    st.session_state['physio_name']=''
                    st.session_state['mobile_number']=0

                    success_message = st.empty()  # Create a placeholder for the success message
                    success_message.success("Data Saved Successfully!")  # Display the success message
                    time.sleep(3)  # Set the duration (e.g., 3 seconds)
                    success_message.empty()  # Clear the message after the duration
                    st.experimental_rerun()


                else:
                    success_message = st.empty()  # Create a placeholder for the success message
                    success_message.success("Data could not be saved!")  # Display the success message
                    time.sleep(2)  # Set the duration (e.g., 3 seconds)
                    success_message.empty()  # Clear the message after the duration
        except:
            st.error("Error adding patient data")



        else:
            st.error("Please fill out all fields with valid data.")







