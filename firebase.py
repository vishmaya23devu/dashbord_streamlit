import streamlit as st
import firebase_admin
from firebase_admin import credentials
import json
import requests
import app

def initialize_firebase_app():
    global cred
    if not firebase_admin._apps:
        cred = credentials.Certificate(r"C:\Users\Hp\Desktop\mainproject\dashbord_streamlit\dashboard-7f2fd-dacb0e6361d5.json")
        firebase_admin.initialize_app(cred)

initialize_firebase_app()

def sign_up_with_email_and_password(email, password, username=None, return_secure_token=True):
    try:
        rest_api_url = "https://identitytoolkit.googleapis.com/v1/accounts:signUp"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": return_secure_token
        }
        if username:
            payload["displayName"] = username
        payload = json.dumps(payload)
        r = requests.post(rest_api_url, params={"key": "AIzaSyApr-etDzcGcsVcmaw7R7rPxx3A09as7uw"}, data=payload)
        r.raise_for_status()  # Raise an exception for HTTP errors
        data = r.json()
        user_info = {
            'email': data['email'],
            'username': data.get('displayName')  # Retrieve username if available
        }
        return user_info
    except requests.exceptions.HTTPError as http_err:
        if r.status_code == 400 and 'EMAIL_EXISTS' in r.json()['error']['message']:
            st.warning('Email already exists. Please use a different email address.')
        else:
            st.warning(f'Signup failed: {http_err}')
    except Exception as e:
        st.warning(f'Signup failed: {e}')

def main():
    st.sidebar.title('Welcome to :violet[Dash-Forge]')

    if 'username' not in st.session_state:
        st.session_state.username = ''
    if 'usermail' not in st.session_state:
        st.session_state.usermail = ''

    def sign_in_with_email_and_password(email=None, password=None, return_secure_token=True):
        rest_api_url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"

        try:
            payload = {
                "returnSecureToken": return_secure_token
            }
            if email:
                payload["email"] = email
            if password:
                payload["password"] = password
            payload = json.dumps(payload)
            r = requests.post(rest_api_url, params={"key": "AIzaSyApr-etDzcGcsVcmaw7R7rPxx3A09as7uw"}, data=payload)
            r.raise_for_status()  # Raise an exception for HTTP errors
            data = r.json()
            user_info = {
                'email': data['email'],
                'username': data.get('displayName')  # Retrieve username if available
            }
            return user_info
        except requests.exceptions.HTTPError as http_err:
            if r.status_code == 400 and 'EMAIL_EXISTS' in r.json()['error']['message']:
                st.warning('Email already exists. Please use a different email address.')
            else:
                st.warning(f'Signup failed: {http_err}')
        except Exception as e:
                st.warning(f'Signin failed: {e}')

    def f():
        try:
            userinfo = sign_in_with_email_and_password(st.session_state.email_input, st.session_state.password_input)
            st.session_state.username = userinfo['username']
            st.session_state.useremail = userinfo['email']
            global Usernm
            Usernm = (userinfo['username'])

            st.session_state.signedout = True
            st.session_state.signout = True
        except:
            st.warning('Login Failed')

    def t():
        st.session_state.signout = False
        st.session_state.signedout = False
        st.session_state.username = ''

    if "signedout" not in st.session_state:
        st.session_state["signedout"] = False
    if 'signout' not in st.session_state:
        st.session_state['signout'] = False

    if not st.session_state["signedout"]:  # only show if the state is False, hence the button has never been clicked
        choice = st.sidebar.selectbox('Login/Signup', ['Login', 'Sign up'])
        email = st.sidebar.text_input('Email Address')
        password = st.sidebar.text_input('Password', type='password')
        st.session_state.email_input = email
        st.session_state.password_input = password

        if choice == 'Sign up':
            username = st.sidebar.text_input("Enter  your unique username")

            if st.sidebar.button('Create my account'):
                user = sign_up_with_email_and_password(email=email, password=password, username=username)
                st.success('Account created successfully!')
                st.markdown('Please Login using your email and password')

        else:
            st.sidebar.button('Login', on_click=f)

    if st.session_state.signout:
        st.sidebar.button('Sign out', on_click=t)
        app.dash()

main()
