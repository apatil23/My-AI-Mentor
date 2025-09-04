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
        # Build context about the user
        user_context = f"""
        User Profile:
        - Name: {user_data.get('name', 'User')}
        - Experience Level: {user_data.get('experience_level', 'Beginner')}
        - Interests: {user_data.get('interests', 'Not specified')}
        - Current Skills: {user_data.get('skills', 'Not specified')}
        - Time Commitment: {user_data.get('time_commitment', 'Not specified')}
        - Learning Style: {user_data.get('learning_style', 'Mixed approach')}
        - Short-term Goals: {user_data.get('short_term_goals', 'Not specified')}
        - Long-term Goals: {user_data.get('long_term_goals', 'Not specified')}
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
            projects_data = json.loads(response.text)
            
            # Ensure we return a list
            if isinstance(projects_data, dict):
                projects_data = [projects_data]
            
            return projects_data
        
        return []
    
    except Exception as e:
        logging.error(f"Error generating project suggestions: {str(e)}")
        return []

def generate_learning_roadmap(roadmap_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a personalized learning roadmap using Gemini API."""
    
    try:
        user_data = roadmap_data['user_data']
        
        prompt = f"""
        You are an expert learning strategist. Create a comprehensive, personalized learning roadmap for the following user and goal.

        User Profile:
        - Name: {user_data.get('name', 'User')}
        - Experience Level: {user_data.get('experience_level', 'Beginner')}
        - Current Skills: {user_data.get('skills', 'Not specified')}
        - Interests: {user_data.get('interests', 'Not specified')}
        - Learning Style: {roadmap_data.get('learning_style', 'Mixed approach')}
        - Time Commitment: {roadmap_data.get('time_per_week', '1-3 hours')} per week

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
        
        # Build conversation context
        conversation_context = ""
        if chat_history:
            conversation_context = "\n".join([
                f"{'User' if msg['role'] == 'user' else 'Mentor'}: {msg['content']}"
                for msg in chat_history[-5:]  # Last 5 messages
            ])
        
        system_prompt = f"""
        You are an expert AI learning mentor and career advisor. You help students and professionals learn new skills, solve problems, and advance their careers in technology.

        User Profile:
        - Name: {user_data.get('name', 'User')}
        - Experience Level: {user_data.get('experience_level', 'Beginner')}
        - Skills: {user_data.get('skills', 'Not specified')}
        - Interests: {user_data.get('interests', 'Not specified')}
        - Goals: {user_data.get('short_term_goals', 'Not specified')}

        Your personality and approach:
        - Friendly, encouraging, and supportive
        - Patient and understanding of different learning paces
        - Practical and focused on actionable advice
        - Knowledgeable about current technology trends
        - Good at breaking down complex concepts
        - Motivational and inspiring

        Guidelines for responses:
        1. Be conversational and personable
        2. Provide specific, actionable advice
        3. Ask clarifying questions when needed
        4. Suggest concrete next steps
        5. Reference the user's profile and goals when relevant
        6. Keep responses focused and not too lengthy
        7. Include examples and analogies when helpful
        8. Be encouraging about their progress and potential

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
                max_output_tokens=1000
            )
        )
        
        return response.text or "I apologize, but I'm having trouble processing your message right now. Could you please try rephrasing your question?"
    
    except Exception as e:
        logging.error(f"Error in chat with mentor: {str(e)}")
        return "I'm experiencing some technical difficulties right now. Please try again in a moment, or check your API key configuration."

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
