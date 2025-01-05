import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader


st.title("Register")
st.markdown("<style>h1{color: #00FFFF; font-size: 48px; font-weight: bold; text-align: center;}</style>", unsafe_allow_html=True)

# Apply custom CSS
with open("authentication.yml") as file:
    config = yaml.load(file, Loader=SafeLoader)

config['patient_list'] = []
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized']
)

try:
    email_of_registered_user, username_of_registered_user, name_of_registered_user = authenticator.register_user(pre_authorization=False)
    config['credentials']['usernames'][username_of_registered_user]['patients'] = []
    if email_of_registered_user:
        st.success('User registered successfully')
except Exception as e:
    st.error(e)
with open("authentication.yml", 'w') as file:
    yaml.dump(config, file, default_flow_style=False)
