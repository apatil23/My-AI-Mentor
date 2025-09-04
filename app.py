import streamlit as st
import pandas as pd
from utils.auth import init_session_state, is_authenticated
from utils.data_manager import init_data_files

# Initialize data files and session state
init_data_files()
init_session_state()

# Page configuration
st.set_page_config(
    page_title="AI Learning Mentor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
    }
    .feature-card {
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin: 1rem 0;
    }
    .hero-section {
        text-align: center;
        padding: 3rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Landing Page
    st.markdown('<div class="hero-section">', unsafe_allow_html=True)
    
    st.title("🎓 AI Learning Mentor")
    st.markdown("### Your Personalized AI-Powered Learning Companion")
    
    st.markdown("""
    Transform your learning journey with intelligent project suggestions, 
    personalized roadmaps, and 24/7 AI mentorship guidance.
    """)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Features section
    st.markdown("## ✨ Key Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>🎯 Smart Project Suggestions</h4>
            <p>Get AI-curated project recommendations based on your interests and skill level</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>🗺️ Personalized Roadmaps</h4>
            <p>Receive custom learning paths tailored to your goals and current expertise</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h4>🤖 AI Chatbot Mentor</h4>
            <p>Get instant help, guidance, and answers to your learning questions</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Authentication section
    st.markdown("## 🚀 Get Started")
    
    if not is_authenticated():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.info("👋 Welcome! Please sign up or log in to access your personalized learning experience.")
            
            if st.button("🔐 Go to Login/Signup", type="primary", use_container_width=True):
                st.switch_page("pages/1_Login.py")
    else:
        st.success(f"Welcome back, {st.session_state.user_data['name']}!")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎯 Get Project Suggestions", type="primary", use_container_width=True):
                st.switch_page("pages/3_Project_Suggestions.py")
        
        with col2:
            if st.button("🗺️ View Learning Roadmap", use_container_width=True):
                st.switch_page("pages/4_Learning_Roadmap.py")
        
        col3, col4 = st.columns(2)
        with col3:
            if st.button("💬 Chat with AI Mentor", use_container_width=True):
                st.switch_page("pages/5_Chatbot_Mentor.py")
        
        with col4:
            if st.button("📊 Track Progress", use_container_width=True):
                st.switch_page("pages/6_Progress_Tracking.py")
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 🧭 Navigation")
        
        if is_authenticated():
            st.markdown(f"**Logged in as:** {st.session_state.user_data['name']}")
            st.markdown("---")
            
            if st.button("👤 Profile Setup"):
                st.switch_page("pages/2_Profile_Setup.py")
            
            if st.button("🎯 Project Suggestions"):
                st.switch_page("pages/3_Project_Suggestions.py")
            
            if st.button("🗺️ Learning Roadmap"):
                st.switch_page("pages/4_Learning_Roadmap.py")
            
            if st.button("💬 Chatbot Mentor"):
                st.switch_page("pages/5_Chatbot_Mentor.py")
            
            if st.button("📊 Progress Tracking"):
                st.switch_page("pages/6_Progress_Tracking.py")
            
            st.markdown("---")
            if st.button("🚪 Logout"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        else:
            if st.button("🔐 Login/Signup"):
                st.switch_page("pages/1_Login.py")
        
        st.markdown("---")
        st.markdown("### 📝 About")
        st.markdown("""
        This AI Learning Mentor helps you discover projects, 
        create learning roadmaps, and provides personalized guidance 
        throughout your learning journey.
        """)

if __name__ == "__main__":
    main()
