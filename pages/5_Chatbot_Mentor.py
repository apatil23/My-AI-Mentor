import streamlit as st
from utils.auth import init_session_state, require_auth, is_authenticated
from utils.gemini_client import chat_with_mentor
from utils.data_manager import save_chat_message, load_chat_history

st.set_page_config(page_title="AI Mentor Chat - AI Learning Mentor", page_icon="💬")

init_session_state()
require_auth()

st.title("💬 AI Learning Mentor Chat")
st.markdown("Get instant help, guidance, and answers to your learning questions!")

if not is_authenticated():
    st.error("Please log in to access this page.")
    st.stop()

user_data = st.session_state.user_data

# Initialize chat session
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []

# Load chat history
chat_history = load_chat_history(user_data['email'])
if not chat_history.empty and not st.session_state.chat_messages:
    # Load recent messages
    recent_messages = chat_history.tail(20)  # Last 20 messages
    for _, message in recent_messages.iterrows():
        st.session_state.chat_messages.append({
            "role": message['role'],
            "content": message['content'],
            "timestamp": message['timestamp']
        })

# Quick start options
if not st.session_state.chat_messages:
    st.header("🚀 Quick Start")
    st.markdown("Choose a topic to get started, or type your own question below:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🎯 Project Help", use_container_width=True):
            starter_message = "I need help with a project. Can you guide me through the planning and development process?"
            st.session_state.chat_messages.append({"role": "user", "content": starter_message, "timestamp": ""})
            st.rerun()
        
        if st.button("🐛 Debugging Help", use_container_width=True):
            starter_message = "I'm having trouble debugging my code. Can you help me understand common debugging techniques?"
            st.session_state.chat_messages.append({"role": "user", "content": starter_message, "timestamp": ""})
            st.rerun()
    
    with col2:
        if st.button("🗺️ Learning Path", use_container_width=True):
            starter_message = "I want to create a learning plan. Can you help me structure my studies effectively?"
            st.session_state.chat_messages.append({"role": "user", "content": starter_message, "timestamp": ""})
            st.rerun()
        
        if st.button("💼 Career Advice", use_container_width=True):
            starter_message = "I'd like career guidance in tech. Can you help me understand different career paths and requirements?"
            st.session_state.chat_messages.append({"role": "user", "content": starter_message, "timestamp": ""})
            st.rerun()
    
    with col3:
        if st.button("🛠️ Technology Choice", use_container_width=True):
            starter_message = "I'm confused about which technology to learn next. Can you help me choose based on my goals?"
            st.session_state.chat_messages.append({"role": "user", "content": starter_message, "timestamp": ""})
            st.rerun()
        
        if st.button("📚 Study Techniques", use_container_width=True):
            starter_message = "What are the best techniques for learning programming effectively? I want to improve my study habits."
            st.session_state.chat_messages.append({"role": "user", "content": starter_message, "timestamp": ""})
            st.rerun()

# Handle context from other pages
if st.session_state.get('chat_context') and not any(msg['content'] == st.session_state.chat_context for msg in st.session_state.chat_messages):
    context_message = st.session_state.chat_context
    st.session_state.chat_messages.append({"role": "user", "content": context_message, "timestamp": ""})
    del st.session_state.chat_context
    st.rerun()

# Chat interface
st.header("💭 Conversation")

# Display chat messages
chat_container = st.container()
with chat_container:
    for i, message in enumerate(st.session_state.chat_messages):
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
                if message.get("timestamp"):
                    st.caption(f"Sent: {message['timestamp']}")
        else:
            with st.chat_message("assistant"):
                st.write(message["content"])
                if message.get("timestamp"):
                    st.caption(f"AI Mentor: {message['timestamp']}")
                
                # Action buttons for AI responses
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    if st.button("👍 Helpful", key=f"helpful_{i}"):
                        st.success("Thanks for the feedback!")
                
                with col2:
                    if st.button("🔄 Clarify", key=f"clarify_{i}"):
                        clarification = f"Can you clarify or expand on this response: '{message['content'][:100]}...'"
                        st.session_state.chat_messages.append({"role": "user", "content": clarification, "timestamp": ""})
                        st.rerun()

# User input
user_input = st.chat_input("Ask me anything about learning, projects, or technology...")

if user_input:
    # Add user message to chat
    st.session_state.chat_messages.append({
        "role": "user", 
        "content": user_input, 
        "timestamp": st.session_state.get('current_time', '')
    })
    
    # Save user message
    save_chat_message({
        'user_email': user_data['email'],
        'role': 'user',
        'content': user_input,
        'timestamp': st.session_state.get('current_time', '')
    })
    
    # Get AI response
    with st.spinner("🤖 AI Mentor is thinking..."):
        try:
            # Prepare context for AI
            context = {
                'user_profile': user_data,
                'chat_history': st.session_state.chat_messages[-5:],  # Last 5 messages for context
                'current_message': user_input
            }
            
            ai_response = chat_with_mentor(context)
            
            if ai_response:
                # Add AI response to chat
                st.session_state.chat_messages.append({
                    "role": "assistant", 
                    "content": ai_response, 
                    "timestamp": st.session_state.get('current_time', '')
                })
                
                # Save AI message
                save_chat_message({
                    'user_email': user_data['email'],
                    'role': 'assistant',
                    'content': ai_response,
                    'timestamp': st.session_state.get('current_time', '')
                })
                
                st.rerun()
            else:
                st.error("Sorry, I couldn't process your message right now. Please try again.")
        
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Sidebar with chat management
with st.sidebar:
    st.header("💬 Chat Management")
    
    st.markdown(f"**Messages in conversation:** {len(st.session_state.chat_messages)}")
    
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_messages = []
        st.success("Chat history cleared!")
        st.rerun()
    
    if st.button("💾 Export Chat"):
        chat_text = ""
        for msg in st.session_state.chat_messages:
            role = "You" if msg["role"] == "user" else "AI Mentor"
            chat_text += f"{role}: {msg['content']}\n\n"
        
        st.download_button(
            label="📥 Download Chat",
            data=chat_text,
            file_name=f"chat_history_{user_data['email']}_{st.session_state.get('current_time', 'export')}.txt",
            mime="text/plain"
        )
    
    st.markdown("---")
    
    # Quick actions
    st.subheader("🎯 Quick Actions")
    
    if st.button("📊 View Progress", use_container_width=True):
        st.switch_page("pages/6_Progress_Tracking.py")
    
    if st.button("🎯 Get Projects", use_container_width=True):
        st.switch_page("pages/3_Project_Suggestions.py")
    
    if st.button("🗺️ View Roadmap", use_container_width=True):
        st.switch_page("pages/4_Learning_Roadmap.py")
    
    if st.button("👤 Update Profile", use_container_width=True):
        st.switch_page("pages/2_Profile_Setup.py")
    
    st.markdown("---")
    
    # Conversation starters
    st.subheader("💡 Conversation Starters")
    
    starters = [
        "What should I learn next?",
        "Help me debug this error",
        "Explain this concept to me",
        "Review my project idea",
        "Career advice in tech",
        "Best learning resources",
        "How to stay motivated?",
        "Technical interview prep"
    ]
    
    for starter in starters:
        if st.button(f"💬 {starter}", key=f"starter_{starter[:10]}"):
            st.session_state.chat_messages.append({"role": "user", "content": starter, "timestamp": ""})
            st.rerun()

# Navigation
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("← Back to Roadmap"):
        st.switch_page("pages/4_Learning_Roadmap.py")

with col2:
    if st.button("🏠 Home"):
        st.switch_page("app.py")

with col3:
    if st.button("📊 Progress Tracking"):
        st.switch_page("pages/6_Progress_Tracking.py")
