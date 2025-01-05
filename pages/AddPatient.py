import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import pandas as pd
import os
from streamlit_extras.switch_page_button import switch_page

if st.button("Back to Homepage"):
    switch_page("Homepage")

class Patient:
    def __init__(self, name, age, gender, nii_file_paths=None, has_heart_disease="Unknown", blood_pressures=None, blood_pressure_dates=None, email=None, medications=None):
        self.name = name
        self.age = age
        self.gender = gender
        self.nii_file_paths = nii_file_paths if nii_file_paths is not None else []
        self.has_heart_disease = has_heart_disease
        self.blood_pressures = blood_pressures if blood_pressures is not None else []
        self.blood_pressure_dates = blood_pressure_dates if blood_pressure_dates is not None else []
        self.email = email
        self.medications = medications if medications is not None else []

with open("authentication.yml") as file:
    config = yaml.load(file, Loader=SafeLoader)
st.title("Add/Edit Patients")
st.markdown("<style>h1{color: #00FFFF; font-size: 48px; font-weight: bold; text-align: center;}</style>", unsafe_allow_html=True)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized']
)

if st.session_state["authentication_status"]:
    name = st.text_input("Enter patient name")
    age = st.number_input("Enter patient age")
    gender = st.radio("Select patient gender", ["Male", "Female"])  
    email = st.text_input("Enter patient email")

    st.subheader("Upload MRI files")
    uploaded_files = st.file_uploader("Choose NII files", accept_multiple_files=True)

    nii_file_paths = [] 
    if uploaded_files:
        os.makedirs("nii_files", exist_ok=True)

        for file in uploaded_files:
            file_path = os.path.join("nii_files", file.name)
            with open(file_path, "wb") as f:
                f.write(file.getvalue())
            nii_file_paths.append(file_path)

    has_heart_disease = st.radio("Does the patient have heart disease?", ["Yes", "No", "Unknown"])

    st.subheader("Upload Blood Pressure Data (CSV)")
    blood_pressure_data = st.file_uploader("Choose CSV file")
    if blood_pressure_data is not None:
        blood_pressure_df = pd.read_csv(blood_pressure_data)
        if 'Systolic' in blood_pressure_df.columns and 'Diastolic' in blood_pressure_df.columns and 'Date' in blood_pressure_df.columns:
            blood_pressures = blood_pressure_df[['Systolic', 'Diastolic']].values.tolist()
            blood_pressure_dates = blood_pressure_df['Date'].tolist()
        else:
            st.warning("CSV file must contain 'Systolic', 'Diastolic', and 'Date' columns.")
            blood_pressures = []
            blood_pressure_dates = []
    else:
        blood_pressures = []
        blood_pressure_dates = []

    medications = st.text_area("Enter medications (one per line)").split('\n')

    if st.button("Add Patient"):
        username_of_registered_user = st.session_state['username']  

        existing_patient = None
        for patient in config['credentials']['usernames'][username_of_registered_user]['patients']:
            if patient['name'] == name:
                existing_patient = patient
                break

        if existing_patient:
            existing_patient.update({
                'age': age,
                'gender': gender,
                'nii_file_paths': nii_file_paths,
                'has_heart_disease': has_heart_disease,
                'blood_pressures': blood_pressures,
                'blood_pressure_dates': blood_pressure_dates,
                'email': email,
                'medications': medications
            })
            st.success("Patient information updated successfully")
        else:
            new_patient = Patient(name, age, gender, nii_file_paths, has_heart_disease, blood_pressures, blood_pressure_dates, email, medications)
            config['credentials']['usernames'][username_of_registered_user]['patients'].append(vars(new_patient))
            st.success("New patient added successfully")

    with open("authentication.yml", 'w') as file:
        yaml.dump(config, file, default_flow_style=False)
