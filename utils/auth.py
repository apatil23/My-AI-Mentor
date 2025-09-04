import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime
from utils.data_manager import load_users, save_user

def hash_password(password: str) -> str:
    """Hash a password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

def init_session_state():
    """Initialize session state variables."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {}
    
    if 'current_time' not in st.session_state:
        st.session_state.current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def is_authenticated() -> bool:
    """Check if user is authenticated."""
    return st.session_state.get('authenticated', False)

def require_auth():
    """Redirect to login if not authenticated."""
    if not is_authenticated():
        st.warning("Please log in to access this page.")
        if st.button("Go to Login", type="primary"):
            st.switch_page("pages/1_Login.py")
        st.stop()

def authenticate_user(email: str, password: str) -> dict | None:
    """Authenticate user with email and password."""
    try:
        users_df = load_users()
        
        if users_df.empty:
            return None
        
        # Find user by email
        user_row = users_df[users_df['email'] == email]
        
        if user_row.empty:
            return None
        
        user_data = user_row.iloc[0].to_dict()
        stored_password = user_data.get('password', '')
        
        # Check password (support both hashed and plain text for backward compatibility)
        if stored_password == password or stored_password == hash_password(password):
            # Remove password from returned data for security
            user_data.pop('password', None)
            return user_data
        
        return None
    
    except Exception as e:
        st.error(f"Authentication error: {str(e)}")
        return None

def register_user(user_data: dict) -> bool:
    """Register a new user."""
    try:
        # Hash the password before storing
        user_data['password'] = hash_password(user_data['password'])
        
        # Save user to CSV
        return save_user(user_data)
    
    except Exception as e:
        st.error(f"Registration error: {str(e)}")
        return False

def logout_user():
    """Log out the current user."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    st.success("Logged out successfully!")
    st.rerun()
