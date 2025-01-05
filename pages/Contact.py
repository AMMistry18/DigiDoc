import os
import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from streamlit_extras.switch_page_button import switch_page

if st.button("Back to Homepage"):
    switch_page("Homepage")
with open("authentication.yml") as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized']
)

if st.session_state["authentication_status"]:
    user_data = {
        "name": st.session_state.get("name"),
        "email": config['credentials']['usernames'][st.session_state.get("username")]['email']
    }
    st.session_state.user_data = user_data

    patient_names = [patient['name'] for patient in config['credentials']['usernames'][st.session_state.get("username")]['patients']]

    st.title("Contact Patients")
    st.markdown("<style>h1{color: #00FFFF; font-size: 48px; font-weight: bold; text-align: center;}</style>", unsafe_allow_html=True)


    selected_patient = st.selectbox("Select patient:", patient_names)

    def send_email(name, email, subject, message):
        sender_email = st.session_state.user_data["email"]
        password = 'xlmw hphz pfug psxl'
        receiver_email = email

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject

        body = f"Dear {name},\n\n{message}\n\nSincerely,\n{st.session_state.user_data['name']}"
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()

    subject = st.text_input("Subject")
    message = st.text_area("Message")

    if st.button("Submit"):
        patient_email = [patient['email'] for patient in config['credentials']['usernames'][st.session_state.get("username")]['patients'] if patient['name'] == selected_patient][0]
        send_email(selected_patient, patient_email, subject, message)
        st.success("Email sent successfully!")
