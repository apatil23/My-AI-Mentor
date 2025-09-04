import streamlit as st
import pandas as pd
from utils.auth import authenticate_user, register_user, init_session_state
from utils.data_manager import load_users, save_user

st.set_page_config(page_title="Login - AI Learning Mentor", page_icon="🔐")

init_session_state()

st.title("🔐 Login / Sign Up")

# Create tabs for login and signup
tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])

with tab1:
    st.header("Welcome Back!")
    
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        if st.form_submit_button("Login", type="primary", use_container_width=True):
            if email and password:
                user_data = authenticate_user(email, password)
                if user_data:
                    st.session_state.authenticated = True
                    st.session_state.user_data = user_data
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid email or password. Please try again.")
            else:
                st.error("Please fill in all fields.")

with tab2:
    st.header("Create Your Account")
    
    with st.form("signup_form"):
        name = st.text_input("Full Name", placeholder="Enter your full name")
        email = st.text_input("Email", placeholder="Enter your email address")
        password = st.text_input("Password", type="password", placeholder="Create a password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
        
        # Basic profile information
        st.markdown("**Tell us a bit about yourself:**")
        experience_level = st.selectbox(
            "Experience Level",
            ["Beginner", "Intermediate", "Advanced", "Expert"]
        )
        
        if st.form_submit_button("Create Account", type="primary", use_container_width=True):
            if name and email and password and confirm_password:
                if password != confirm_password:
                    st.error("Passwords do not match.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters long.")
                else:
                    # Check if user already exists
                    users_df = load_users()
                    if email in users_df['email'].values:
                        st.error("An account with this email already exists.")
                    else:
                        # Register new user
                        user_data = {
                            'name': name,
                            'email': email,
                            'password': password,
                            'experience_level': experience_level,
                            'interests': '',
                            'skills': '',
                            'goals': '',
                            'created_at': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        
                        if register_user(user_data):
                            st.session_state.authenticated = True
                            st.session_state.user_data = user_data
                            st.success("Account created successfully! Welcome to AI Learning Mentor!")
                            st.rerun()
                        else:
                            st.error("Failed to create account. Please try again.")
            else:
                st.error("Please fill in all fields.")

# If user is authenticated, redirect to profile setup or home
if st.session_state.authenticated:
    st.balloons()
    st.success(f"Welcome, {st.session_state.user_data['name']}!")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🏠 Go to Home", use_container_width=True):
            st.switch_page("app.py")
    
    with col2:
        if st.button("👤 Complete Profile Setup", type="primary", use_container_width=True):
            st.switch_page("pages/2_Profile_Setup.py")

# Back to home button
if st.button("← Back to Home"):
    st.switch_page("app.py")
