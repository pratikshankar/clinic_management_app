import streamlit as st
import sqlite3
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pdfkit
import os


# Database Connection
def connect_db():
    conn = sqlite3.connect("patients.db")
    return conn


# Fetch patient data based on patient ID
def fetch_patient_data(patient_id):
    conn = connect_db()
    query = "SELECT name, service, sessions, amount_paid FROM Patients WHERE id = ?"
    patient_data = pd.read_sql_query(query, conn, params=(patient_id,))
    conn.close()
    return patient_data


# Generate Bill as HTML
def generate_bill_html(patient_data, session_cost):
    name = patient_data['name'].iloc[0]
    service = patient_data['service'].iloc[0]
    sessions = patient_data['sessions'].iloc[0]
    amount_paid = patient_data['amount_paid'].iloc[0]

    total_cost = session_cost * sessions
    balance_due = total_cost - amount_paid

    # Create an HTML template for the bill
    html = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
            }}
            .bill-container {{
                width: 80%;
                margin: 0 auto;
                border: 2px solid #ccc;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            }}
            h2 {{
                color: #4CAF50;
                text-align: center;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            table, th, td {{
                border: 1px solid #ddd;
            }}
            th, td {{
                padding: 10px;
                text-align: left;
            }}
            th {{
                background-color: #4CAF50;
                color: white;
            }}
            .total {{
                text-align: right;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="bill-container">
            <h2>Patient Bill</h2>
            <p><strong>Patient Name:</strong> {name}</p>
            <p><strong>Service Taken:</strong> {service}</p>
            <p><strong>Number of Sessions:</strong> {sessions}</p>
            <table>
                <tr>
                    <th>Details</th>
                    <th>Amount</th>
                </tr>
                <tr>
                    <td>Cost per Session</td>
                    <td>₹{session_cost}</td>
                </tr>
                <tr>
                    <td>Total Cost</td>
                    <td>₹{total_cost}</td>
                </tr>
                <tr>
                    <td>Amount Paid</td>
                    <td>₹{amount_paid}</td>
                </tr>
                <tr>
                    <td>Balance Due</td>
                    <td>₹{max(balance_due, 0)}</td>
                </tr>
            </table>
        </div>
    </body>
    </html>
    """
    return html


# Send email with bill attachment
def send_email(to_email, subject, body, pdf_path):
    sender_email = "your_email@gmail.com"  # Replace with your email
    password = "your_password"  # Replace with your email app password

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Add body text
    msg.attach(MIMEText(body, 'plain'))

    # Attach the PDF
    with open(pdf_path, "rb") as attachment:
        part = MIMEText(attachment.read(), 'base64', 'utf-8')
        part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(pdf_path))
        msg.attach(part)

    # Send email
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.send_message(msg)
        st.success("Email sent successfully!")
    except Exception as e:
        st.error(f"Failed to send email: {e}")


# Streamlit App
st.title("Professional Billing System with Email")

# Input for Patient ID
patient_id = st.text_input("Enter Patient ID:")
email = st.text_input("Enter Patient Email Address:")

if patient_id:
    patient_data = fetch_patient_data(patient_id)

    if not patient_data.empty:
        st.write("### Patient Details")
        st.table(patient_data)

        session_cost = st.number_input("Enter Cost per Session:", min_value=0, step=100, value=500)

        if st.button("Generate Bill"):
            # Generate Bill HTML
            bill_html = generate_bill_html(patient_data, session_cost)
            st.markdown(bill_html, unsafe_allow_html=True)

            # Save Bill as PDF
            pdf_path = "patient_bill.pdf"
            pdfkit.from_string(bill_html, pdf_path)

            st.success("Bill generated successfully!")
            st.download_button("Download Bill as PDF", open(pdf_path, "rb"), file_name="bill.pdf",
                               mime="application/pdf")

            # Email the Bill
            if email:
                subject = "Your Bill from Pain Easy Clinic"
                body = "Please find the attached bill for your recent sessions at Pain Easy Clinic."
                send_email(email, subject, body, pdf_path)
