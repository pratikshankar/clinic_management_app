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
import datetime
from utils import fetch_appointment_counts
from utils import read_patient_data
from utils import generate_time_slots
from utils import schedule_appointment_with_dropdown
load_dotenv()
st.set_page_config(layout="wide")


db_path = os.getenv('db_path')
create_table(db_path)

if 'appointment_date' not in st.session_state:
    st.session_state['appointment_date']=datetime.datetime.now().date()
if 'create_appointment_date' not in st.session_state:
    st.session_state['create_appointment_date']=datetime.datetime.now().date()

# Add a title to your app
st.title("Welcome to  Pain Easy's patient management app!")

col1,col2=st.columns([1,1])
with col1:
    st.subheader('View Today\'s appointments')
    st.session_state.appointment_date=st.date_input("Session Date", value=st.session_state.appointment_date)
    query='''Select a.patient_name ,b.patient_mob_number ,DATE(a.appointment_time) as apointment_date , TIME(a.appointment_time) as appointment_time , a.status from Appointments a
    left join patients b
    on a.patient_id=b.patient_id
    where apointment_date=?
    '''
    st.write(read_patient_data(db_path, query, params=(st.session_state.appointment_date)))
with col2:
    st.subheader('Schedule a new appointment')
    schedule_appointment_with_dropdown(db_path)
    # query = '''Select * from Appointments'''
    # st.write(read_patient_data(db_path, query))
