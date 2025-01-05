import streamlit as st
import yaml
from yaml.loader import SafeLoader
import plotly.graph_objects as go
from streamlit_extras.switch_page_button import switch_page

with open("authentication.yml") as file:
    config = yaml.load(file, Loader=SafeLoader)

st.title("Patient Viewer")
st.markdown("<style>h1{color: #00FFFF; font-size: 48px; font-weight: bold; text-align: center;}</style>", unsafe_allow_html=True)

patients = config['credentials']['usernames'][st.session_state.get("username")]['patients']

button_labels = ["Add/Edit Patient", "Contact", "AI Heart Disease Prediction", "AI MRI Segmenter"]

container = st.container()

with st.container():
    col1, col2, col3, col4 = st.columns((1, 1, 1, 1))
    button_style = "<style>div.stButton > button { width: 100%; height: 50px; }</style>"

    with col1:
        st.markdown(button_style, unsafe_allow_html=True)
        if st.button("Add/Edit Patient", key="add_patient_button"):
            switch_page("AddPatient")

    with col2:
        st.markdown(button_style, unsafe_allow_html=True)
        if st.button("Contact", key="contact_button"):
            switch_page("Contact")

    with col3:
        st.markdown(button_style, unsafe_allow_html=True)
        if st.button("AI Disease Predictor", key="ai_heart_disease_prediction_button"):
            switch_page("Heart Disease Prediction")

    with col4:
        st.markdown(button_style, unsafe_allow_html=True)
        if st.button("AI MRI Segmenter", key="ai_mri_segmenter_button"):
            switch_page("MRI Scans")


def apply_styles():
    st.markdown("""
    <style>
    /* Tile styling */
    .stCard {
        background-color: #e0f7fa; 
        border: 2px solid #4db6ac; 
        border-radius: 15px;
        padding: 20px;
        margin: 10px;
        box-shadow: 0 4px 8px rgba(0, 150, 136, 1.0); 
        transition: transform 0.3s ease-in-out; 
        position: relative;
        overflow: hidden;
        width: 100%;
    }
    
    .stCard h1 {
        color: #00695c; 
        font-size: 24px;
        margin-bottom: 10px;
    }
    .stCard p {
        color: #00796b; 
    }
    
    .stCard:hover {
        transform: translateY(-5px); 
        box-shadow: 0 6px 12px rgba(0, 150, 136, 1.5); 
    }
    
    .stCard::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background-color: rgba(0, 150, 136, 0.1); 
        transform: rotate(45deg);
        pointer-events: none;
        transition: opacity 0.3s ease-in-out;
        z-index: 0;
    }
    .stCard:hover::before {
        opacity: 0; 
    }
    </style>
    """, unsafe_allow_html=True)

apply_styles()

def display_patient_info(selected_patient_data):
    name = selected_patient_data["name"]
    col1, col2, col3 = st.columns((1, 1, 1))
    with st.container():
        with col1:
            a = selected_patient_data["email"]
            st.markdown(f"<div class='stCard'><h1>Email</h1><p>{a}</p></div>", unsafe_allow_html=True)
        with col2:
            meds = selected_patient_data["medications"]
            if len(meds) <= 0:
                st.markdown(f"<div class='stCard'><h1>No\nMedications</h1></div>", unsafe_allow_html=True)
            else:
                a = ", ".join(meds)
                st.markdown(f"<div class='stCard'><h1>Medications</h1><p>{a}</p></div>", unsafe_allow_html=True)
                a = int(selected_patient_data["age"])
            st.markdown(f"<div class='stCard'><h1>Age</h1><p>{a}</p></div>", unsafe_allow_html=True)
        with col3:
            if (selected_patient_data["gender"] == "Male"):
                st.image("maleIcon.png", caption="Sex: Male")
            else:
                st.image("femaleIcon.png", caption="Sex: Female")

            has_hd = selected_patient_data["has_heart_disease"]=='Yes'
            a = selected_patient_data["has_heart_disease"]
            with col1:
                st.markdown(f"<div class='stCard'><h1>Heart Disease</h1><p>{a}</p></div>", unsafe_allow_html=True)


with open("authentication.yml") as file:
    config = yaml.safe_load(file)

username = st.session_state.get("username")

if username and username in config['credentials']['usernames']:
    patients = config['credentials']['usernames'][username]['patients']
else:
    patients = []

selected_patient = st.selectbox("Select Patient", [""] + [patient['name'] for patient in patients])
if selected_patient:
    selected_patient_data = next((patient for patient in patients if patient['name'] == selected_patient), None)
    if selected_patient_data == None:
        st.write("Patient not found.")
    else:
        st.write("Selected Patient Data:")
        display_patient_info(selected_patient_data)
        
        st.write("\n")

        bp_dates = selected_patient_data["blood_pressure_dates"]
        bp_systolic = [bp[0] for bp in selected_patient_data["blood_pressures"]]
        bp_diastolic = [bp[1] for bp in selected_patient_data["blood_pressures"]]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=bp_dates, y=bp_systolic, mode='lines', name='Systolic', line=dict(color='red')))
        fig.add_trace(go.Scatter(x=bp_dates, y=bp_diastolic, mode='lines', name='Diastolic', line=dict(color='blue')))
        fig.update_layout(title='Blood Pressure Measurements', xaxis_title='Date', yaxis_title='Blood Pressure')
        
        st.plotly_chart(fig)
