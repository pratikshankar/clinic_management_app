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
import os
import re
import datetime




def check_number(mobile_number):
    if mobile_number.isdigit() and len(mobile_number) == 10:
        return(True,f"Mobile Number: {mobile_number}")
    else:
        return(False,"Please enter a valid 10-digit mobile number.")


def create_table(db_name):
    try:
        # Connect to SQLite database (or create it if it doesn't exist)
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Create a new table in the database based on the DataFrame's column names
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Patients (
        patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT NOT NULL,
        patient_mob_number TEXT UNIQUE NOT NULL,
        patient_address TEXT NOT NULL,
        total_sessions INTEGER,
        sessions_completed INTEGER DEFAULT 0,
        sessions_left INTEGER,
        amount_paid REAL,
        source TEXT,
        physio_name TEXT NOT NULL 
    )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Sessions (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                session_date DATE ,
                physio_comments TEXT,
                patient_comments TEXT,
                patient_progress INTEGER,
                session_cancelled TEXT,
                reason_of_cancellation TEXT,
                FOREIGN KEY (patient_id) REFERENCES Patients (patient_id),
                UNIQUE(patient_id, session_date)
            )
        ''')

        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS Appointments (
                    appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER DEFAULT NULL,
                    patient_name TEXT,
                    session_id INTEGER DEFAULT NULL,
                    appointment_time DATETIME NOT NULL,
                    status TEXT CHECK(status IN ('Scheduled', 'Completed', 'Canceled', 'Rescheduled')) DEFAULT 'Scheduled',
                    cancellation_reason TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id),
                    FOREIGN KEY (session_id) REFERENCES Sessions(session_id)
                    
                    )
                ''')

        conn.commit()
        conn.close()
        print(f"Data saved successfully.")
    except Exception as e:
        print(f"Error saving data to SQLite: {e}")

def save_patient_data(db_name,query,params=()):
    try:

        # Connect to SQLite database
        pat_conn = sqlite3.connect(db_name)
        cursor = pat_conn.cursor()
        # Query the table and load the data into a pandas DataFrame
        # Ensure params is a tuple (even for a single parameter like selected_video)
        if not isinstance(params, tuple):
            params = (params,)
        print("Executing query:", query)
        print("With parameters:", params)
        cursor.execute(query, params)
        pat_conn.commit()
        pat_conn.close()
        st.success("data added successfully!")
        return True
    except sqlite3.IntegrityError:
        conn.close()
        st.error("Data already exists in the database.")
        return False
    except sqlite3.OperationalError as e:
        st.error(f"Error")
        return False
    except Exception as e:
        st.error(f"An error occurred")
        return False




def save_sessions_data(db_name,query,params=()):
    try:

        # Connect to SQLite database
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        # Query the table and load the data into a pandas DataFrame
        # Ensure params is a tuple (even for a single parameter like selected_video)
        if not isinstance(params, tuple):
            params = (params,)
        print("Executing query:", query)
        print("With parameters:", params)
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        st.success("data added successfully!")
        return True
    except sqlite3.IntegrityError:
        st.error("Data already exists in the database.")
        return False
    except sqlite3.OperationalError as e:
        st.error(f"Error")
        return False
    except Exception as e:
        st.error(f"An error occurred")
        return False


def read_patient_data(db_name,query,params=()):
    try:
        conn = sqlite3.connect(db_name)
        # Query the table and load the data into a pandas DataFrame
        # Ensure params is a tuple (even for a single parameter like selected_video)
        if not isinstance(params, tuple):
            params = (params,)
        print("Executing query:", query)
        print("With parameters:", params)
        df = pd.read_sql_query(query, conn, params=params)
        # Close the connection
        conn.close()
        print(f"Data read successfully")
        return df
    except Exception as e:
        print(f"Error reading data from SQLite: {e}")
        return None

def fetch_appointment_counts(db_path, date):
    """Fetch the number of appointments per 30-minute interval for the selected date."""
    conn = sqlite3.connect(db_path)
    query = f"""
        SELECT strftime('%H:%M', appointment_time) AS interval, COUNT(*) AS count
        FROM Appointments
        WHERE date(appointment_time) = ?
        GROUP BY interval
    """
    df = pd.read_sql_query(query, conn, params=(date,))
    conn.close()
    return df

def generate_time_slots(selected_date):
    start_time = datetime.datetime.combine(selected_date, datetime.time(0, 0))
    end_time = datetime.datetime.combine(selected_date, datetime.time(23, 59))
    slots = []
    while start_time <= end_time:
        slots.append(start_time)
        start_time += datetime.timedelta(minutes=30)
    return slots

def schedule_appointment_with_dropdown(db_path):
    # Select a date
    selected_date = st.date_input("Select Date for Appointment", datetime.date.today())

    # Fetch appointments count for the selected date
    appointment_counts = fetch_appointment_counts(db_path, selected_date)

    # Convert counts to a dictionary for easy lookup
    count_dict = {row['interval']: row['count'] for _, row in appointment_counts.iterrows()}

    # Generate 30-minute time slots
    time_slots = generate_time_slots(selected_date)

    # Build dropdown options with color-coded availability
    dropdown_options = []
    for slot in time_slots:
        slot_key = slot.strftime('%H:%M')
        appointment_count = count_dict.get(slot_key, 0)

        # Determine slot status
        if appointment_count < 2:
            color = "🟢"  # Green circle emoji
            status = "Available"
        elif appointment_count == 2:
            color = "🟡"  # Yellow circle emoji
            status = "Limited"
        else:
            color = "🔴"  # Red circle emoji
            status = "Full"

        # Format dropdown option
        dropdown_options.append(
            f"{color} {slot.strftime('%I:%M %p')} - {status} ({appointment_count}/3)"
        )

    # Show the dropdown for selecting a time slot
    selected_slot = st.selectbox("Select an Appointment Slot", dropdown_options)

    # Parse the selected slot to extract the datetime
    selected_time_index = dropdown_options.index(selected_slot)
    selected_datetime = time_slots[selected_time_index]
    st.session_state.search_name = st.text_input("Type a first name:")
    if st.session_state.search_name:
        query = '''
               SELECT patient_id, patient_name, patient_mob_number
               FROM patients 
               WHERE patient_name LIKE ?
               '''
        results = read_patient_data(db_path, query, params=(st.session_state.search_name))
        if not results.empty:
            results["display"] = results["patient_name"] + " (" + results["patient_mob_number"] + ")"

            selected_display = st.selectbox(
                "Select the name you are looking for:",
                results["display"]
            )
            if selected_display:
                selected_row = results[results["display"] == selected_display]
                patient_id = int(selected_row["patient_id"].values[0])
                phone_number = selected_row["patient_mob_number"].values[0]
                full_name = selected_row["patient_name"].values[0]
        if results.empty:

            patient_id=None
            full_name=st.session_state.search_name

    # Allow booking if the slot is available
    if "Full" not in selected_slot:
        if st.button("Book Appointment"):
            # Save the appointment in the database
            conn = sqlite3.connect(db_path)
            query = """
                INSERT INTO Appointments (appointment_time, status,patient_id,patient_name) VALUES (?, 'Scheduled',?,?)
            """
            if isinstance(patient_id, int):
                patient_id=int(patient_id)

            print(full_name)
            conn.execute(query, (selected_datetime,patient_id,full_name))
            conn.commit()
            conn.close()
            st.success("Appointment scheduled successfully!")
            st.experimental_rerun()
    else:
        st.error("This time slot is fully booked. Please select another slot.")


# def update_appointment_state(db_path,new_state):







