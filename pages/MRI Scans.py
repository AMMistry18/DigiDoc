import nibabel as nib
import cv2
import numpy as np
from tensorflow.keras.models import load_model
import streamlit as st
import yaml
from PIL import Image
import io
from streamlit_extras.switch_page_button import switch_page
from nilearn.plotting import view_img
from skimage.transform import downscale_local_mean
import joblib
import os

import matplotlib.pyplot as plt
import plotly.graph_objs as go

st.title("AI Segmenter")
st.markdown("<style>h1{color: #00FFFF; font-size: 48px; font-weight: bold; text-align: center;}</style>", unsafe_allow_html=True)

def hash_file_path(file_path):
    return os.path.splitext(file_path)[0].replace("/", "_").replace("\\", "_")

def load_yaml(file_path):
    cache_path = f"{hash_file_path(file_path)}.joblib"
    if os.path.exists(cache_path):
        return joblib.load(cache_path)
    with open(file_path, "r") as file:
        data = yaml.safe_load(file)
        joblib.dump(data, cache_path)
        return data

data = load_yaml("authentication.yml")

def load_cnn_model(model_path):
    cache_path = f"{hash_file_path(model_path)}.joblib"
    if os.path.exists(cache_path):
        return joblib.load(cache_path)
    model = load_model(model_path)
    joblib.dump(model, cache_path)
    return model

cnn_model = load_cnn_model('tsaModel.h5')

def preprocess_mri(img):
    img = cv2.equalizeHist(img)
    
    mri_image = cv2.resize(img, (256, 256))
    
    return mri_image

def display_3d_view(img_data):
    
    downsample_factor = 4  
    img_data_downsampled = downscale_local_mean(img_data, (downsample_factor, downsample_factor, downsample_factor))

    x, y, z = np.indices(img_data_downsampled.shape)
    fig = go.Figure(data=go.Volume(
        x=x.flatten(),
        y=y.flatten(),
        z=z.flatten(),
        value=img_data_downsampled.flatten(),
        isomin=img_data_downsampled.min(),
        isomax=img_data_downsampled.max(),
        opacity=0.1,  
        surface_count=10,  
        colorscale='Gray' 
    ))

    fig.update_layout(scene=dict(
        xaxis=dict(nticks=10, range=[0, img_data_downsampled.shape[0]]),
        yaxis=dict(nticks=10, range=[0, img_data_downsampled.shape[1]]),
        zaxis=dict(nticks=10, range=[0, img_data_downsampled.shape[2]]),
    ))

    st.plotly_chart(fig)

if st.button("Back to Homepage"):
    switch_page("Homepage")

username = st.session_state.get("username")

if username and username in data['credentials']['usernames']:
    patients = data['credentials']['usernames'][username]['patients']
else:
    patients = []

patient_mri_files = {patient['name']: patient['nii_file_paths'] for patient in patients}

selected_patient = st.selectbox("Select Patient", [""] + list(patient_mri_files.keys()))
if selected_patient:
    patient_mri_files_selected = patient_mri_files[selected_patient]
    
    selected_file = st.selectbox("Select MRI File", [""] + patient_mri_files_selected)
    if selected_file:
        def load_mri_file(file_path):
            cache_path = f"{hash_file_path(file_path)}.joblib"
            if os.path.exists(cache_path):
                return joblib.load(cache_path)
            nii_img = nib.load(file_path)
            img_data = nii_img.get_fdata()
            joblib.dump(img_data, cache_path)
            return img_data
        
        img_data = load_mri_file(selected_file)
        middle_slice = img_data[:, :, img_data.shape[2] // 2]
        normalized_img = cv2.normalize(middle_slice, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        mri_image = preprocess_mri(normalized_img)

        predicted_mask = cnn_model.predict(np.expand_dims(mri_image, axis=0)).squeeze()

        predicted_mask_normalized = (predicted_mask - predicted_mask.min()) / (predicted_mask.max() - predicted_mask.min())

        cmap = plt.get_cmap('jet')  
        inverted_cmap = cmap.reversed()  

        colored_heatmap = inverted_cmap(predicted_mask_normalized)[:, :, :3]  
        st.subheader("Original MRI File")
        display_3d_view(img_data)

        st.subheader("Sliced MRI with Left Atrium")
        st.image(mri_image, caption='Sliced MRI with Left Atrium', use_column_width=True)
        st.subheader("Segmented Left Atrium")
        st.image(colored_heatmap, caption='Segmented Left Atrium', use_column_width=True)
