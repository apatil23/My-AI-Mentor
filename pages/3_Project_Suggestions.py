import streamlit as st
from utils.auth import init_session_state, require_auth, is_authenticated
from utils.gemini_client import generate_project_suggestions
from utils.data_manager import save_user_interaction

st.set_page_config(page_title="Project Suggestions - AI Learning Mentor", page_icon="🎯")

init_session_state()
require_auth()

st.title("🎯 AI-Powered Project Suggestions")
st.markdown("Get personalized project recommendations based on your profile and interests!")

if not is_authenticated():
    st.error("Please log in to access this page.")
    st.stop()

user_data = st.session_state.user_data

# Display user context
with st.expander("📋 Your Profile Summary", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Experience Level:** {user_data.get('experience_level', 'Not set')}")
        st.write(f"**Time Commitment:** {user_data.get('time_commitment', 'Not set')}")
        st.write(f"**Learning Style:** {user_data.get('learning_style', 'Not set')}")
    
    with col2:
        interests = user_data.get('interests', 'Not set')
        skills = user_data.get('skills', 'Not set')
        st.write(f"**Interests:** {interests[:100]}{'...' if len(interests) > 100 else ''}")
        st.write(f"**Skills:** {skills[:100]}{'...' if len(skills) > 100 else ''}")

# Project generation form
st.header("🎨 Generate Custom Projects")

with st.form("project_generation_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        focus_area = st.selectbox(
            "Focus Area",
            [
                "Based on my profile",
                "Programming & Software Development",
                "Data Science & Analytics",
                "Web Development",
                "Mobile App Development",
                "Machine Learning & AI",
                "Game Development",
                "UI/UX Design",
                "Digital Marketing",
                "Business & Entrepreneurship",
                "Creative Arts",
                "Science & Research"
            ]
        )
        
        difficulty_level = st.selectbox(
            "Difficulty Level",
            ["Beginner", "Intermediate", "Advanced", "Mixed levels"]
        )
    
    with col2:
        project_type = st.selectbox(
            "Project Type",
            [
                "Any type",
                "Portfolio projects",
                "Learning exercises",
                "Real-world applications",
                "Open source contributions",
                "Freelance/Client work",
                "Research projects",
                "Creative challenges"
            ]
        )
        
        timeline = st.selectbox(
            "Preferred Timeline",
            ["1-2 weeks", "1 month", "2-3 months", "3-6 months", "Flexible"]
        )
    
    num_projects = st.slider("Number of projects to generate", 1, 5, 3)
    
    additional_requirements = st.text_area(
        "Additional Requirements (optional)",
        placeholder="Any specific requirements, technologies, or constraints for your projects?"
    )
    
    generate_button = st.form_submit_button("🚀 Generate Project Suggestions", type="primary", use_container_width=True)

# Generate and display projects
if generate_button or st.session_state.get('show_projects'):
    if generate_button:
        with st.spinner("🤖 AI is generating personalized projects for you..."):
            try:
                projects = generate_project_suggestions(
                    user_data=user_data,
                    focus_area=focus_area,
                    difficulty_level=difficulty_level,
                    project_type=project_type,
                    timeline=timeline,
                    num_projects=num_projects,
                    additional_requirements=additional_requirements
                )
                
                if projects:
                    st.session_state.generated_projects = projects
                    st.session_state.show_projects = True
                    
                    # Save interaction
                    interaction_data = {
                        'user_email': user_data['email'],
                        'interaction_type': 'project_suggestion',
                        'details': f"Generated {num_projects} projects for {focus_area}",
                        'timestamp': st.session_state.get('current_time', '')
                    }
                    save_user_interaction(interaction_data)
                else:
                    st.error("Failed to generate projects. Please try again.")
            
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.error("Please check your API key configuration and try again.")
    
    # Display generated projects
    if st.session_state.get('generated_projects'):
        st.header("🎉 Your Personalized Projects")
        
        projects = st.session_state.generated_projects
        
        # Video recommendations based on focus area
        focus_area_videos = {
            "Programming & Software Development": {
                "title": "Complete Python Programming Course",
                "video_id": "rfscVS0vtbw",
                "description": "Full Python course for beginners to advanced"
            },
            "Data Science & Analytics": {
                "title": "Data Science Full Course",
                "video_id": "ua-CiDNNj30",
                "description": "Complete data science tutorial with Python"
            },
            "Web Development": {
                "title": "Full Stack Web Development Course",
                "video_id": "nu_pCVPKzTk",
                "description": "Complete web development bootcamp"
            },
            "Mobile App Development": {
                "title": "React Native Full Course",
                "video_id": "0-S5a0eXPoc",
                "description": "Build mobile apps with React Native"
            },
            "Machine Learning & AI": {
                "title": "Machine Learning Full Course",
                "video_id": "GwIo3gDZCVQ",
                "description": "Complete machine learning course"
            },
            "Game Development": {
                "title": "Unity Game Development Tutorial",
                "video_id": "XtQMytORBmM",
                "description": "Learn game development with Unity"
            },
            "UI/UX Design": {
                "title": "UI/UX Design Complete Course",
                "video_id": "c9Wg6Cb_YlU",
                "description": "Master UI/UX design principles"
            },
            "Digital Marketing": {
                "title": "Digital Marketing Full Course",
                "video_id": "bixR-KIJKYM",
                "description": "Complete digital marketing strategy"
            },
            "Business & Entrepreneurship": {
                "title": "Entrepreneurship and Business",
                "video_id": "ZoqgAy3h4OM",
                "description": "Learn business fundamentals"
            },
            "Creative Arts": {
                "title": "Digital Art and Design Course",
                "video_id": "AdKuh5_NzpI",
                "description": "Creative digital art techniques"
            },
            "Science & Research": {
                "title": "Research Methodology Course",
                "video_id": "wbhXHKHPmXs",
                "description": "Scientific research methods"
            }
        }
        
        # Show recommended video for the focus area
        if focus_area != "Based on my profile" and focus_area in focus_area_videos:
            st.subheader(f"📺 Recommended Learning Video for {focus_area}")
            
            video_info = focus_area_videos[focus_area]
            
            col1, col2 = st.columns([2, 1])
            with col1:
                # Embed YouTube video
                st.video(f"https://www.youtube.com/watch?v={video_info['video_id']}")
            
            with col2:
                st.markdown(f"**🎬 {video_info['title']}**")
                st.markdown(f"📖 {video_info['description']}")
                st.markdown("💡 *This video provides foundational knowledge for your selected focus area*")
            
            st.markdown("---")
        
        for i, project in enumerate(projects, 1):
            with st.container():
                st.markdown(f"### 🚀 Project {i}: {project.get('title', f'Project {i}')}")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Description:** {project.get('description', 'No description available')}")
                    
                    if project.get('objectives'):
                        st.markdown("**Learning Objectives:**")
                        for objective in project.get('objectives', []):
                            st.markdown(f"• {objective}")
                    
                    if project.get('technologies'):
                        st.markdown(f"**Technologies:** {', '.join(project.get('technologies', []))}")
                    
                    if project.get('features'):
                        st.markdown("**Key Features:**")
                        for feature in project.get('features', []):
                            st.markdown(f"• {feature}")
                
                with col2:
                    st.markdown(f"**⏱️ Timeline:** {project.get('timeline', 'Not specified')}")
                    st.markdown(f"**📊 Difficulty:** {project.get('difficulty', 'Not specified')}")
                    
                    if project.get('resources'):
                        with st.expander("📚 Resources"):
                            for resource in project.get('resources', []):
                                st.markdown(f"• {resource}")
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button(f"📋 Save Project {i}", key=f"save_{i}"):
                        # Save to user's saved projects
                        saved_projects = st.session_state.get('saved_projects', [])
                        if project not in saved_projects:
                            saved_projects.append(project)
                            st.session_state.saved_projects = saved_projects
                            st.success(f"Project {i} saved!")
                
                with col2:
                    if st.button(f"🗺️ Create Roadmap", key=f"roadmap_{i}"):
                        st.session_state.selected_project_for_roadmap = project
                        st.switch_page("pages/4_Learning_Roadmap.py")
                
                with col3:
                    if st.button(f"💬 Discuss with AI", key=f"discuss_{i}"):
                        st.session_state.chat_context = f"I want to discuss this project: {project.get('title', 'Untitled Project')}"
                        st.switch_page("pages/5_Chatbot_Mentor.py")
                
                st.markdown("---")
        
        # Regenerate button
        if st.button("🔄 Generate More Projects", type="secondary"):
            del st.session_state['generated_projects']
            st.session_state.show_projects = False
            st.rerun()

# Saved projects section
if st.session_state.get('saved_projects'):
    st.header("💾 Your Saved Projects")
    
    saved_projects = st.session_state.saved_projects
    
    for i, project in enumerate(saved_projects):
        with st.expander(f"📋 {project.get('title', f'Saved Project {i+1}')}"):
            st.markdown(f"**Description:** {project.get('description', 'No description')}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"🗺️ Create Roadmap", key=f"saved_roadmap_{i}"):
                    st.session_state.selected_project_for_roadmap = project
                    st.switch_page("pages/4_Learning_Roadmap.py")
            
            with col2:
                if st.button(f"🗑️ Remove", key=f"remove_{i}"):
                    st.session_state.saved_projects.pop(i)
                    st.rerun()

# Navigation
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("← Back to Profile"):
        st.switch_page("pages/2_Profile_Setup.py")

with col2:
    if st.button("🗺️ Learning Roadmap"):
        st.switch_page("pages/4_Learning_Roadmap.py")

with col3:
    if st.button("💬 Chat with Mentor"):
        st.switch_page("pages/5_Chatbot_Mentor.py")
