import streamlit as st
import streamlit_authenticator as stauth
from streamlit_extras.switch_page_button import switch_page
import yaml
from yaml.loader import SafeLoader

with open("authentication.yml") as file:
    config = yaml.load(file, Loader=SafeLoader)


st.markdown(
    """
    <style>
    body {
        font-family: Arial, sans-serif;
        color: #00FFFF; 
        background-color: white;
    }
    .title {
        font-size: 48px;
        font-weight: bold;
        text-align: center;
        color: #00FFFF; 
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<p class="title">Digi-Doc</p>', unsafe_allow_html=True)
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized']
)

authenticator.login()

if st.session_state["authentication_status"]:
    switch_page("homepage") 
    st.session_state["authentication_status"] = None  

elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')

elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')
