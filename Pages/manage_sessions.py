import streamlit as st
import os
import pandas as pd
from datetime import date
from dotenv import load_dotenv
from utils import check_number, create_table, read_patient_data, save_patient_data,save_sessions_data
from st_aggrid import AgGrid, GridOptionsBuilder
from datetime import datetime

st.set_page_config(layout="wide")
load_dotenv()

# Initialize database path and create table if not exists
db_path = os.getenv('db_path')
create_table(db_path)

# Initialize session state variables for persistence
if 'patient_name' not in st.session_state:
    st.session_state['patient_name'] = ''
if 'sessions' not in st.session_state:
    st.session_state['sessions'] = []
if 'exists' not in st.session_state:
    st.session_state['exists'] = 0
if 'session_date' not in st.session_state:
    st.session_state['session_date'] = date.today()
if 'patient_address' not in st.session_state:
    st.session_state['patient_address'] = ''
if 'physio_remarks' not in st.session_state:
    st.session_state['physio_remarks']=''
if 'patient_remarks' not in st.session_state:
    st.session_state['patient_remarks']=''

if 'is_saved' not in st.session_state:
    st.session_state['is_saved']=False

if 'is_extended'  not in st.session_state:
    st.session_state['is_extended']=0

if 'selected_date' not in st.session_state:
    st.session_state['selected_date']=datetime.now().date()

if 'selected_time' not in st.session_state:
    st.session_state['selected_time']=datetime.now().time()

if 'schedule_appointment' not in st.session_state:
    st.session_state['schedule_appointment']=False

if  'is_app_created' not in st.session_state:
    st.session_state['is_app_created']=False

if  'data_present' not in st.session_state:
    st.session_state['data_present']=False

if 'mobile_number' not in st.session_state:
    st.session_state['mobile_number']=''

# Title
st.title("Patient Registration Portal")

# Input field for mobile number
st.session_state.mobile_number = st.text_input(
    "Enter Patient's mobile number:",
    value=st.session_state.mobile_number,  # Fetch the stored value
    key="mobile_number_input",  # Key for this input
)
# st.write("st.session_state.mobile_number",st.session_state.mobile_number)
valid_number, response = check_number(st.session_state.mobile_number)

# Check if patient exists based on mobile number

if st.button("Check Details!") :
    query = 'SELECT * FROM Patients WHERE patient_mob_number=?'
    params = st.session_state.mobile_number
    st.session_state.patients_data = read_patient_data(db_path, query, params)
    patient_id = st.session_state.patients_data['patient_id'].values[0]
    query_sess = 'SELECT * FROM Sessions WHERE patient_id=?'
    params_sess = (int(patient_id),)
    st.session_state.sesion_df=read_patient_data(db_path,query_sess,params_sess)
    #st.write(st.session_state.sesion_df)
    if not st.session_state.patients_data.empty:
        st.session_state.exists = 1
    else:
        st.session_state.exists = 0  # Reset exists state if patient not found

    if not st.session_state.sesion_df.empty:
        #st.write(st.session_state.sesion_df)
        st.session_state.patient_progress = st.session_state.sesion_df['patient_progress'].values[-1]
        print("st.session_state.patient_progress",st.session_state.patient_progress)
    else:
        st.session_state.patient_progress = 0  # Reset exists state if patient not found
# Display and handle adding session info if patient exists
if st.session_state.exists == 1 and st.session_state.mobile_number != '':
    # Get patient details and show summary
    # patient_data = st.session_state.patients_data[
    #     st.session_state.patients_data['patient_mob_number'] == mobile_number]
    left_col_info, right_col_info = st.columns([1, 2])
    with left_col_info :
        print("st.session_state.patients_data",st.session_state.patients_data)
        print("st.session_state.patients_data",type(st.session_state.patients_data))
        try:

            patient_id = st.session_state.patients_data['patient_id'].values[0]
            st.write(f"**Patient patient_id:** {st.session_state.patients_data['patient_id'].values[0]}")
            st.write(f"**Patient name:** {st.session_state.patients_data['patient_name'].values[0]}")
            st.write(f"**Total Sessions:** {st.session_state.patients_data['total_sessions'].values[0]}")
            # st.session_state.patient_progress=st.session_state.patients_data['patient_progress'].values[0]
            st.markdown(
                f"<span style='color: green;'>**Sessions Completed:** {st.session_state.patients_data['sessions_completed'].values[0]}</span>",
                unsafe_allow_html=True)
            st.markdown(
                f"<span style='color: red;'>**Sessions Left:** {st.session_state.patients_data['sessions_left'].values[0]}</span>",
                unsafe_allow_html=True)
            st.session_state.data_present=True
        except:
            st.session_state.data_present=False
            st.error("Enter patient's number to continue")
    if st.session_state.data_present:

        with right_col_info :

            st.markdown(
                """
                <style>
                .fixed-table-container {
                    width: 1000px;  /* Fixed width for the table container */
                    # height: 0px; /* Fixed height for the table container */
                    overflow-y: auto;  /* Enable vertical scrolling */
                    overflow-x: auto;  /* Enable horizontal scrolling */
                }
                </style>
                """,
                unsafe_allow_html=True
            )
            st.markdown('<div class="fixed-table-container">', unsafe_allow_html=True)
            st.dataframe(st.session_state.sesion_df.drop(columns={'patient_id','session_cancelled','reason_of_cancellation'}).sort_values(by='session_id'), use_container_width=True)  # Interactive table
            st.markdown('</div>', unsafe_allow_html=True)


            # st.table(st.session_state.sesion_df.drop(columns={'patient_id'}))

        left_col, right_col = st.columns([1, 1])
        with left_col :

            # Session details input with persistent date and address
            st.session_state.session_date = st.date_input("Session Date", value=st.session_state.session_date)
            st.session_state.physio_remarks = st.text_input("Enter Physio's Remarks:", value=st.session_state.physio_remarks)
            st.session_state.patient_remarks= st.text_input("Enter Patient's Remarks:", value=st.session_state.patient_remarks)
            st.session_state.patient_progress=st.slider("Select Patient's Progress",
        min_value=1,
        max_value=10,
        value=st.session_state.patient_progress,  # Default session
        step=1,
        key='progress_slider')





            # Button to add session data

            if st.button("Add Session") and st.session_state.patients_data['sessions_left'].values[0]>=1:
                # Insert new session record and update patient session counts in database
                query_session = '''
                    INSERT INTO Sessions (patient_id, session_date, physio_comments,patient_comments,patient_progress)
                    VALUES (?, ?, ?,?,?)
                '''
                print("paramenets of add sessiom",patient_id)
                params_session = (int(patient_id), st.session_state.session_date, st.session_state.physio_remarks,st.session_state.patient_remarks,int(st.session_state.patient_progress))
                query='Select * from Patients where patient_id=?'
                params=(int(patient_id))
                df_temp=read_patient_data(db_path, query,params)
                sessions_left=df_temp['sessions_left'].values[0]
                print("sessions_left=",sessions_left)
                if sessions_left>0:
                    st.session_state.is_saved=save_sessions_data(db_path, query_session, params_session)
                    if st.session_state.is_saved:
                        print("Session added successfully!")
                        update_query = '''
                            UPDATE Patients
                            SET sessions_completed = sessions_completed+1,
                                sessions_left = total_sessions-sessions_completed-1
                            WHERE patient_id = ? and (total_sessions-sessions_completed-1)>=0
                        '''
                        save_patient_data(db_path, update_query, (int(patient_id),))
                        query = 'select * from Sessions'
                        st.write(read_patient_data(db_path, query))

                    # Show success message and reset address field for a fresh session
                        st.success("Session details added and counts updated successfully!")
                        st.session_state.patient_progress=0
                        st.session_state.patient_remarks=''
                        st.session_state.physio_remarks=''
                        # st.session_state.mobile_number=''
                        # st.session_state.patients_data=None


                        st.experimental_rerun()
                else:
                    st.error("Sessions already completed !")


            elif st.session_state.patients_data['sessions_left'].values[0]<0:
                st.error("Sessions Completed !")
        with right_col :
            if st.button("Click to Extend Sessions!") and st.session_state.patients_data['sessions_left'].values[0] <= 1:
                st.session_state.is_extended = 1

            if st.session_state.is_extended == 1:

                extended_sessions = st.number_input("Number of added sessions signed Up For", min_value=0, step=1, value=0,
                                                    key='total_sessions')
                amount_paid_extension = st.number_input("Enter amount Paid:", value=0, key='amount_paid')
                update_payment_query = '''
                Update 
                Patients
                SET
                total_sessions = total_sessions + ?,sessions_left= sessions_left + ?, amount_paid=amount_paid + ?
                WHERE
                patient_id = ?;'''
                if st.button("Extend Sessions!") and st.session_state.is_extended:
                    params_extension = (extended_sessions, extended_sessions, amount_paid_extension, int(patient_id))
                    st.session_state.is_saved = save_sessions_data(db_path, update_payment_query, params_extension)
                    st.session_state.is_extended = 0
        # if st.button("Schedule next Appointment!") :
        #     st.session_state.schedule_appointment=True
        # if st.session_state.schedule_appointment :
        #
        #     st.session_state.selected_date = st.date_input("Appointment Date", value=st.session_state.selected_date)
        #     st.session_state.selected_time = st.time_input("Appointment Time", value=st.session_state.selected_time)
        #
        #     # Combine into a single datetime
        #     appointment_datetime = datetime.combine(st.session_state.selected_date, st.session_state.selected_time)
        #
        #
        #     app_query=f'''INSERT INTO Appointments (patient_id,appointment_time) values(?,?)'''
        #     app_params=(int(patient_id),appointment_datetime.strftime('%Y-%m-%d %H:%M:%S'))
        #     print("app_params",app_params)
        #     if st.button("Confirm appointment!"):
        #         st.session_state.is_app_created = save_sessions_data(db_path, app_query, app_params)
        #         if st.session_state.is_app_created:
        #             st.success("Appointment created !")
        #             st.session_state.schedule_appointment = False
        #             st.session_state.is_app_created=False
        #
        #
        #         else:
        #             st.error("Error creating appointment !")


    # Display error if no patient data found and mobile number entered
    if st.session_state.exists == 0 or st.session_state.mobile_number=='':
        st.error("No info about this patient!")



