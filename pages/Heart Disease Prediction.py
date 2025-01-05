import pandas as pd
import xgboost as xgb
import streamlit as st
import yaml
from streamlit_extras.switch_page_button import switch_page

if st.button("Back to Homepage"):
    switch_page("Homepage")
with open("authentication.yml") as file:
    config = yaml.load(file, Loader=yaml.SafeLoader)

patient_data = config['credentials']['usernames'][st.session_state.get("username")]['patients']
patient_names = [patient['name'] for patient in patient_data]

st.title("AI Heart Disease Predictor")
st.markdown("<style>h1{color: #00FFFF; font-size: 48px; font-weight: bold; text-align: center;}</style>", unsafe_allow_html=True)

selected_patient = st.selectbox("Select patient:", patient_names)

selected_patient_data = [patient for patient in patient_data if patient['name'] == selected_patient][0]
age = selected_patient_data['age']
gender = selected_patient_data['gender']

sex = 0 if gender.lower() == "female" else 1  

cp = st.selectbox("Chest Pain Type", options=["Asymptomatic", "Atypical Angina", "Non-anginal Pain", "Typical Angina"])
cp_mapping = {"Asymptomatic": 0, "Atypical Angina": 1, "Non-anginal Pain": 2, "Typical Angina": 3}
cp = cp_mapping[cp]
trestbps = st.number_input("Resting Blood Pressure (mmHg)")
chol = st.number_input("Cholesterol (mg/dL)")
fbs = st.radio("Fasting Blood Sugar > 120 mg/dL", options=["No", "Yes"])
fbs = 1 if fbs == "No" else 0
restecg = st.selectbox("Resting Electrocardiographic Results", options=["Probable/Definite LVH", "Normal", "ST-T Wave Abnormality"])
restecg_mapping = {"Probable/Definite LVH": 0, "Normal": 1, "ST-T Wave Abnormality": 2}
restecg = restecg_mapping[restecg]
thalach = st.number_input("Maximum Heart Rate")
exang = st.radio("Exercise Induced Angina", options=["No", "Yes"])
exang = 0 if exang == "No" else 1
oldpeak = st.number_input("ST Depression Induced by Exercise Relative to Rest")
slope = st.selectbox("Slope of Peak Exercise ST Segment", options=["Downsloping", "Flat", "Upsloping"])
slope_mapping = {"Downsloping": 0, "Flat": 1, "Upsloping": 2}
slope = slope_mapping[slope]
ca = st.number_input("Number of Major Vessels (0-3)", min_value=0, max_value=3, step=1)
thal = st.selectbox("Thalassemia", options=["NULL", "Fixed Defect", "Normal", "Reversible Defect"])
thal_mapping = {"NULL": 0, "Fixed Defect": 1, "Normal": 2, "Reversible Defect": 3}
thal = thal_mapping[thal]

new_data_point = {
    'age': age,
    'sex': sex,
    'cp': cp,
    'trestbps': trestbps,
    'chol': chol,
    'fbs': fbs,
    'restecg': restecg,
    'thalach': thalach,
    'exang': exang,
    'oldpeak': oldpeak,
    'slope': slope,
    'ca': ca,
    'thal': thal
}

new_data_point_df = pd.DataFrame([new_data_point])

if st.button("Enter"):
    xgb_model = xgb.XGBClassifier()    
    xgb_model.load_model("heart.json")

    predictions_proba = xgb_model.predict_proba(new_data_point_df)
    prob_heart_disease_present = predictions_proba[0][1]  
    prob_no_heart_disease = predictions_proba[0][0] 

    if prob_heart_disease_present > prob_no_heart_disease:
        prediction = 1
        likelihood = prob_heart_disease_present
    else:
        prediction = 0
        likelihood = prob_no_heart_disease

    has_heart_disease = "Yes" if prediction == 1 else "No"

    with open("authentication.yml", "w") as file:
        yaml.dump(config, file)

    st.write(f"Prediction for patient '{selected_patient}': {'Heart Disease Present' if prediction == 1 else 'No Heart Disease'}")
    st.write(f"Likelihood: {likelihood:.2%}")
