import os
import json
import logging
from google import genai
from google.genai import types
from typing import Dict, Any, List

# Initialize Gemini client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", "default_key"))

def generate_project_suggestions(
    user_data: Dict[str, Any],
    focus_area: str,
    difficulty_level: str,
    project_type: str,
    timeline: str,
    num_projects: int,
    additional_requirements: str = ""
) -> List[Dict[str, Any]]:
    """Generate personalized project suggestions using Gemini API."""
    
    try:
        # Build context about the user with proper data validation
        import pandas as pd
        
        def safe_get(data, key, default):
            value = data.get(key, default)
            if pd.isna(value) or not isinstance(value, str):
                return default
            return value
        
        user_context = f"""
        User Profile:
        - Name: {safe_get(user_data, 'name', 'User')}
        - Experience Level: {safe_get(user_data, 'experience_level', 'Beginner')}
        - Interests: {safe_get(user_data, 'interests', 'Not specified')}
        - Current Skills: {safe_get(user_data, 'skills', 'Not specified')}
        - Time Commitment: {safe_get(user_data, 'time_commitment', 'Not specified')}
        - Learning Style: {safe_get(user_data, 'learning_style', 'Mixed approach')}
        - Short-term Goals: {safe_get(user_data, 'short_term_goals', 'Not specified')}
        - Long-term Goals: {safe_get(user_data, 'long_term_goals', 'Not specified')}
        """
        
        prompt = f"""
        You are an expert learning mentor and project advisor. Based on the user profile below, generate {num_projects} personalized project suggestions.

        {user_context}

        Project Requirements:
        - Focus Area: {focus_area}
        - Difficulty Level: {difficulty_level}
        - Project Type: {project_type}
        - Timeline: {timeline}
        - Additional Requirements: {additional_requirements or 'None'}

        Please generate projects that:
        1. Match the user's skill level and interests
        2. Are achievable within the specified timeline
        3. Provide clear learning outcomes
        4. Include practical, hands-on experience
        5. Are relevant to their career goals

        For each project, provide:
        - Title: A clear, engaging project name
        - Description: A comprehensive overview of the project
        - Learning Objectives: 3-5 specific skills/concepts the user will learn
        - Technologies: List of technologies, tools, and frameworks to be used
        - Key Features: 4-6 main features or components to implement
        - Timeline: Detailed breakdown of time estimates
        - Difficulty: How challenging this project is for the user
        - Resources: Helpful learning resources, tutorials, or documentation links

        Return the response as a JSON array of project objects.
        """
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.7
            )
        )
        
        if response.text:
            try:
                projects_data = json.loads(response.text)
                
                # Ensure we return a list
                if isinstance(projects_data, dict):
                    projects_data = [projects_data]
                
                # Validate that each project has required fields
                validated_projects = []
                for i, project in enumerate(projects_data):
                    if isinstance(project, dict):
                        # Ensure all required fields exist
                        validated_project = {
                            'title': project.get('title', f'Learning Project {i+1}'),
                            'description': project.get('description', 'A hands-on project to develop your skills and apply what you\'ve learned.'),
                            'objectives': project.get('objectives', project.get('learning_objectives', ['Learn new skills', 'Apply knowledge practically', 'Build portfolio project'])),
                            'technologies': project.get('technologies', ['Various tools and frameworks']),
                            'features': project.get('features', project.get('key_features', ['Core functionality', 'User interface', 'Data handling'])),
                            'timeline': project.get('timeline', timeline),
                            'difficulty': project.get('difficulty', difficulty_level),
                            'resources': project.get('resources', ['Online tutorials', 'Documentation', 'Community forums'])
                        }
                        validated_projects.append(validated_project)
                    else:
                        # If project is not a dict, create a basic project structure
                        validated_projects.append({
                            'title': f'Learning Project {i+1}',
                            'description': 'A hands-on project to develop your skills and apply what you\'ve learned.',
                            'objectives': ['Learn new skills', 'Apply knowledge practically', 'Build portfolio project'],
                            'technologies': ['Various tools and frameworks'],
                            'features': ['Core functionality', 'User interface', 'Data handling'],
                            'timeline': timeline,
                            'difficulty': difficulty_level,
                            'resources': ['Online tutorials', 'Documentation', 'Community forums']
                        })
                
                return validated_projects if validated_projects else []
            
            except json.JSONDecodeError:
                logging.warning(f"Failed to parse JSON response: {response.text[:200]}...")
                # Return fallback projects if JSON parsing fails
                return create_fallback_projects(num_projects, focus_area, difficulty_level, timeline)
        
        return create_fallback_projects(num_projects, focus_area, difficulty_level, timeline)
    
    except Exception as e:
        logging.error(f"Error generating project suggestions: {str(e)}")
        return create_fallback_projects(num_projects, focus_area, difficulty_level, timeline)

def create_fallback_projects(num_projects: int, focus_area: str, difficulty_level: str, timeline: str) -> List[Dict[str, Any]]:
    """Create fallback projects when API fails."""
    base_projects = {
        "Programming & Software Development": {
            'title': 'Personal Task Manager Application',
            'description': 'Build a comprehensive task management app with user authentication, task creation, editing, and organization features.',
            'technologies': ['Python/JavaScript', 'Database (SQLite/PostgreSQL)', 'Web Framework', 'HTML/CSS'],
            'features': ['User registration/login', 'Create and edit tasks', 'Task categories and priorities', 'Due date reminders', 'Search and filter functionality']
        },
        "Web Development": {
            'title': 'Interactive Portfolio Website',
            'description': 'Create a modern, responsive portfolio website showcasing your projects and skills with interactive elements.',
            'technologies': ['HTML5', 'CSS3', 'JavaScript', 'React/Vue.js', 'Git'],
            'features': ['Responsive design', 'Project showcase', 'Contact form', 'Blog section', 'Smooth animations']
        },
        "Data Science & Analytics": {
            'title': 'Data Visualization Dashboard',
            'description': 'Build an interactive dashboard that analyzes and visualizes real-world datasets with meaningful insights.',
            'technologies': ['Python', 'Pandas', 'Plotly/Matplotlib', 'Streamlit/Dash', 'Jupyter Notebooks'],
            'features': ['Data cleaning and preprocessing', 'Interactive charts', 'Filter and search capabilities', 'Export functionality', 'Statistical analysis']
        },
        "Mobile App Development": {
            'title': 'Mobile Expense Tracker',
            'description': 'Develop a mobile app to track daily expenses with categorization, budgeting, and spending analysis features.',
            'technologies': ['React Native/Flutter', 'Mobile Database', 'API Integration', 'Push Notifications'],
            'features': ['Expense logging', 'Category management', 'Budget tracking', 'Spending reports', 'Backup and sync']
        }
    }
    
    fallback_projects = []
    for i in range(num_projects):
        # Use focus area specific project or default
        if focus_area in base_projects:
            base_project = base_projects[focus_area].copy()
        else:
            base_project = base_projects["Programming & Software Development"].copy()
        
        base_project.update({
            'title': f"{base_project['title']} {i+1}" if i > 0 else base_project['title'],
            'objectives': ['Learn practical skills', 'Build portfolio project', 'Apply best practices'],
            'timeline': timeline,
            'difficulty': difficulty_level,
            'resources': ['Official documentation', 'Online tutorials', 'Community support']
        })
        
        fallback_projects.append(base_project)
    
    return fallback_projects

def generate_learning_roadmap(roadmap_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a personalized learning roadmap using Gemini API."""
    
    try:
        user_data = roadmap_data['user_data']
        
        # Safe data extraction with validation
        import pandas as pd
        
        def safe_get(data, key, default):
            value = data.get(key, default)
            if pd.isna(value) or not isinstance(value, str):
                return default
            return value
        
        prompt = f"""
        You are an expert learning strategist. Create a comprehensive, personalized learning roadmap for the following user and goal.

        User Profile:
        - Name: {safe_get(user_data, 'name', 'User')}
        - Experience Level: {safe_get(user_data, 'experience_level', 'Beginner')}
        - Current Skills: {safe_get(user_data, 'skills', 'Not specified')}
        - Interests: {safe_get(user_data, 'interests', 'Not specified')}
        - Learning Style: {safe_get(roadmap_data, 'learning_style', 'Mixed approach')}
        - Time Commitment: {safe_get(roadmap_data, 'time_per_week', '1-3 hours')} per week

        Learning Goal: {roadmap_data.get('goal', '')}
        Timeline: {roadmap_data.get('timeline', '3 months')}
        Difficulty Level: {roadmap_data.get('difficulty_level', 'Intermediate')}
        Focus Areas: {', '.join(roadmap_data.get('focus_areas', []))}
        Prior Knowledge: {roadmap_data.get('prior_knowledge', 'Not specified')}
        Additional Preferences: {roadmap_data.get('preferences', 'None')}

        Create a detailed roadmap with:
        1. Title: A motivating title for the learning journey
        2. Overview: A brief description of what the user will achieve
        3. Phases: Break down learning into 3-6 logical phases, each containing:
           - Title: Phase name
           - Duration: Time estimate for this phase
           - Objective: What the user will accomplish
           - Topics: Specific topics/concepts to learn
           - Activities: Practical exercises, projects, or assignments
           - Resources: Recommended books, courses, tutorials, or tools
           - Milestones: Measurable checkpoints to track progress
        4. Additional Resources: Extra materials for deeper learning
        5. Tips: Personalized study tips based on their learning style and schedule

        Make sure the roadmap is:
        - Realistic for their timeline and time commitment
        - Appropriate for their experience level
        - Aligned with their goals and interests
        - Actionable with clear next steps
        - Progressive, building from basic to advanced concepts

        Return as a JSON object.
        """
        
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.6
            )
        )
        
        if response.text:
            return json.loads(response.text)
        
        return {}
    
    except Exception as e:
        logging.error(f"Error generating learning roadmap: {str(e)}")
        return {}

def chat_with_mentor(context: Dict[str, Any]) -> str:
    """Chat with AI mentor using conversation context."""
    
    try:
        user_data = context['user_profile']
        chat_history = context.get('chat_history', [])
        current_message = context['current_message']
        
        # Build conversation context with data validation
        import pandas as pd
        
        conversation_context = ""
        if chat_history:
            conversation_context = "\n".join([
                f"{'User' if msg['role'] == 'user' else 'Mentor'}: {str(msg['content']) if not pd.isna(msg.get('content', '')) else 'No content'}"
                for msg in chat_history[-5:]  # Last 5 messages
                if msg and isinstance(msg, dict)
            ])
        
        # Safe data extraction for user profile
        def safe_get_profile(data, key, default):
            import pandas as pd
            value = data.get(key, default)
            if pd.isna(value) or not isinstance(value, str) or value == '':
                return default
            return value
        
        system_prompt = f"""
        You are an expert AI learning mentor and career advisor. You help students and professionals learn new skills, solve problems, and advance their careers in technology.

        User Profile:
        - Name: {safe_get_profile(user_data, 'name', 'User')}
        - Experience Level: {safe_get_profile(user_data, 'experience_level', 'Beginner')}
        - Skills: {safe_get_profile(user_data, 'skills', 'Not specified')}
        - Interests: {safe_get_profile(user_data, 'interests', 'Not specified')}
        - Goals: {safe_get_profile(user_data, 'short_term_goals', 'Not specified')}

        Your personality and approach:
        - Friendly, encouraging, and supportive
        - Patient and understanding of different learning paces
        - Practical and focused on actionable advice
        - Knowledgeable about current technology trends
        - Good at breaking down complex concepts
        - Motivational and inspiring
        - ALWAYS provide helpful responses to any learning-related question
        - Never refuse to answer questions about projects, coding, or technology

        Guidelines for responses:
        1. Be conversational and personable
        2. Provide specific, actionable advice
        3. Ask clarifying questions when needed
        4. Suggest concrete next steps
        5. Reference the user's profile and goals when relevant
        6. Keep responses focused and helpful
        7. Include examples and analogies when helpful
        8. Be encouraging about their progress and potential
        9. Answer ALL questions related to learning, projects, coding, and technology
        10. If you need more context, ask specific follow-up questions

        Recent conversation context:
        {conversation_context}

        Current user message: {current_message}

        Respond as a helpful mentor would, providing guidance, answering questions, and offering support for their learning journey.
        """
        
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=[
                types.Content(
                    role="user", 
                    parts=[types.Part(text=current_message)]
                )
            ],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7,
                max_output_tokens=1500
            )
        )
        
        # Better response handling
        if response and response.text:
            return response.text.strip()
        else:
            logging.warning(f"Empty response from Gemini for message: {current_message[:100]}")
            return "I understand you're asking about that topic. Let me help you with that! Could you provide a bit more detail about what specifically you'd like to know or what challenge you're facing?"
    
    except Exception as e:
        logging.error(f"Error in chat with mentor: {str(e)}")
        # Try a simpler approach if the complex one fails
        try:
            simple_response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"You are a helpful learning mentor. Answer this question: {current_message}"
            )
            if simple_response and simple_response.text:
                return simple_response.text.strip()
        except:
            pass
        
        return f"I'm here to help with your question: '{current_message[:100]}'. Could you please try asking in a different way? I'm ready to assist with any learning, coding, or project-related topics!"

def analyze_learning_progress(progress_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze user's learning progress and provide insights."""
    
    try:
        prompt = f"""
        Analyze the following learning progress data and provide insights and recommendations.

        Progress Data:
        {json.dumps(progress_data, indent=2)}

        Provide analysis in the following areas:
        1. Learning Patterns: Identify trends in learning activities and time commitment
        2. Strengths: Areas where the user is excelling
        3. Areas for Improvement: Aspects that need more attention
        4. Recommendations: Specific suggestions for next steps
        5. Motivation: Encouraging observations about progress

        Return as a JSON object with these sections.
        """
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.6
            )
        )
        
        if response.text:
            return json.loads(response.text)
        
        return {}
    
    except Exception as e:
        logging.error(f"Error analyzing learning progress: {str(e)}")
        return {}
