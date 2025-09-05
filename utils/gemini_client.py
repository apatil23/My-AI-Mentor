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
        You are an expert learning mentor and project advisor with deep knowledge of popular GitHub projects, industry standards, and real-world applications. Based on the user profile below, generate {num_projects} DIVERSE and UNIQUE personalized project suggestions.

        {user_context}

        Project Requirements:
        - Focus Area: {focus_area}
        - Difficulty Level: {difficulty_level}
        - Project Type: {project_type}
        - Timeline: {timeline}
        - Additional Requirements: {additional_requirements or 'None'}

        IMPORTANT: Each project must be COMPLETELY DIFFERENT from the others. Draw inspiration from:
        - Popular open-source projects on GitHub
        - Real-world industry applications
        - Trending technologies and tools
        - Practical problems people face daily
        - Creative and innovative solutions

        Please generate projects that:
        1. Are UNIQUE and DIVERSE - no similar concepts or features
        2. Match the user's skill level and interests
        3. Are based on real-world, practical applications
        4. Provide clear learning outcomes with specific technologies
        5. Include modern, industry-relevant tools and frameworks
        6. Are achievable within the specified timeline
        7. Offer portfolio-worthy outcomes

        For each project, provide:
        - title: A specific, engaging project name (not generic)
        - description: Detailed overview explaining what the user will build and why it's useful
        - objectives: 3-5 specific, measurable learning outcomes
        - technologies: Specific tools, frameworks, and libraries (not generic terms)
        - features: 4-6 distinct, implementable features that make the project useful
        - timeline: {timeline}
        - difficulty: {difficulty_level}
        - resources: Specific learning resources, documentation, and tutorials

        Examples of GOOD project diversity:
        - A password manager CLI tool with encryption
        - A real-time collaborative whiteboard app
        - A machine learning-powered recommendation system
        - A blockchain-based voting system
        - An AR mobile app for interior design

        Examples of BAD (too similar) projects:
        - Task manager app
        - Todo list application  
        - Project tracking tool
        (These are all task management variations)

        Return ONLY a valid JSON array with NO additional text or formatting.
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
                        # Ensure all required fields exist with better defaults
                        validated_project = {
                            'title': project.get('title', f'Innovative {focus_area} Project {i+1}'),
                            'description': project.get('description', f'A practical {focus_area.lower()} project designed to challenge your skills and create something meaningful for your portfolio.'),
                            'objectives': project.get('objectives', project.get('learning_objectives', [f'Master {focus_area.lower()} fundamentals', 'Build real-world applicable skills', 'Create portfolio-worthy project', 'Learn industry best practices'])),
                            'technologies': project.get('technologies', ['Python', 'JavaScript', 'Git', 'HTML/CSS']),
                            'features': project.get('features', project.get('key_features', [f'Core {focus_area.lower()} functionality', 'User-friendly interface', 'Data management system', 'Performance optimization'])),
                            'timeline': project.get('timeline', timeline),
                            'difficulty': project.get('difficulty', difficulty_level),
                            'resources': project.get('resources', ['Official documentation', 'Online tutorials', 'GitHub examples', 'Stack Overflow'])
                        }
                        validated_projects.append(validated_project)
                    else:
                        # If project is not a dict, use a fallback project from our comprehensive pool
                        validated_projects.append(create_fallback_projects(1, focus_area, difficulty_level, timeline)[0])
                
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
    """Create diverse, realistic projects inspired by popular GitHub and industry projects."""
    
    # Comprehensive project pool organized by category
    project_pool = {
        "Programming & Software Development": [
            {
                'title': 'Password Manager CLI Tool',
                'description': 'Build a secure command-line password manager with encryption, password generation, and secure storage using industry-standard cryptography.',
                'technologies': ['Python', 'Cryptography', 'SQLite', 'Argparse', 'Pytest'],
                'features': ['AES encryption', 'Master password authentication', 'Password generation', 'Secure clipboard integration', 'Import/export functionality'],
                'objectives': ['Learn cryptography basics', 'Master CLI development', 'Understand secure coding practices', 'Build testing workflows']
            },
            {
                'title': 'Real-time Chat Application',
                'description': 'Create a multi-room chat application with real-time messaging, user authentication, and file sharing capabilities using WebSocket technology.',
                'technologies': ['Node.js', 'Socket.io', 'Express', 'MongoDB', 'JWT Authentication'],
                'features': ['Real-time messaging', 'Multiple chat rooms', 'File sharing', 'User status indicators', 'Message history'],
                'objectives': ['Master WebSocket programming', 'Learn real-time communication', 'Implement user authentication', 'Handle file uploads']
            },
            {
                'title': 'URL Shortener Service',
                'description': 'Build a URL shortening service like bit.ly with custom short codes, analytics, expiration dates, and QR code generation.',
                'technologies': ['Python/Flask', 'Redis', 'PostgreSQL', 'Docker', 'Nginx'],
                'features': ['Custom short codes', 'Click analytics', 'QR code generation', 'Bulk URL processing', 'API rate limiting'],
                'objectives': ['Learn system design patterns', 'Implement caching strategies', 'Build RESTful APIs', 'Deploy with containers']
            }
        ],
        "Web Development": [
            {
                'title': 'E-commerce Product Catalog',
                'description': 'Develop a modern e-commerce frontend with product search, filtering, shopping cart, and checkout flow using modern frameworks.',
                'technologies': ['React', 'TypeScript', 'Tailwind CSS', 'Stripe API', 'Context API'],
                'features': ['Product search and filtering', 'Shopping cart management', 'User reviews system', 'Wishlist functionality', 'Payment integration'],
                'objectives': ['Master React hooks and context', 'Learn payment integration', 'Implement responsive design', 'Handle complex state management']
            },
            {
                'title': 'Social Media Dashboard',
                'description': 'Create a comprehensive dashboard to manage multiple social media accounts with post scheduling, analytics, and content management.',
                'technologies': ['Vue.js', 'Node.js', 'Chart.js', 'Social Media APIs', 'MongoDB'],
                'features': ['Multi-platform posting', 'Content calendar', 'Analytics visualization', 'Hashtag suggestions', 'Team collaboration'],
                'objectives': ['Integrate multiple APIs', 'Build data visualization', 'Implement scheduling systems', 'Learn Vue.js ecosystem']
            },
            {
                'title': 'Recipe Sharing Platform',
                'description': 'Build a community-driven recipe sharing platform with user-generated content, ratings, meal planning, and shopping list generation.',
                'technologies': ['Next.js', 'Prisma', 'PostgreSQL', 'AWS S3', 'NextAuth.js'],
                'features': ['Recipe submission and editing', 'User ratings and reviews', 'Meal planning calendar', 'Shopping list generation', 'Nutritional information'],
                'objectives': ['Learn full-stack Next.js', 'Implement file uploads', 'Build user-generated content systems', 'Create complex data relationships']
            }
        ],
        "Data Science & Analytics": [
            {
                'title': 'Stock Market Analysis Tool',
                'description': 'Build a comprehensive stock analysis tool with real-time data, technical indicators, portfolio tracking, and predictive modeling.',
                'technologies': ['Python', 'Pandas', 'Plotly', 'yfinance', 'Scikit-learn', 'Streamlit'],
                'features': ['Real-time stock data', 'Technical indicators', 'Portfolio performance tracking', 'Risk analysis', 'Price prediction models'],
                'objectives': ['Learn financial data analysis', 'Implement machine learning models', 'Build interactive visualizations', 'Handle real-time data streams']
            },
            {
                'title': 'Customer Sentiment Analysis System',
                'description': 'Create a system to analyze customer feedback from multiple sources using NLP techniques to extract sentiment and key insights.',
                'technologies': ['Python', 'NLTK', 'Transformers', 'BeautifulSoup', 'PostgreSQL', 'FastAPI'],
                'features': ['Multi-source data collection', 'Sentiment classification', 'Key phrase extraction', 'Trend analysis', 'Automated reporting'],
                'objectives': ['Master NLP techniques', 'Learn web scraping', 'Implement ML pipelines', 'Build data processing workflows']
            },
            {
                'title': 'Weather Data Analytics Platform',
                'description': 'Develop a platform that collects, processes, and visualizes weather data with predictions, alerts, and historical trend analysis.',
                'technologies': ['Python', 'Apache Airflow', 'PostgreSQL', 'Grafana', 'Weather APIs'],
                'features': ['Automated data collection', 'Weather predictions', 'Alert system', 'Historical trend analysis', 'Geographic visualization'],
                'objectives': ['Learn data pipeline architecture', 'Implement time series analysis', 'Build monitoring systems', 'Create geographic visualizations']
            }
        ],
        "Mobile App Development": [
            {
                'title': 'Habit Tracking App',
                'description': 'Build a mobile app for habit tracking with streaks, reminders, progress visualization, and social sharing features.',
                'technologies': ['React Native', 'AsyncStorage', 'Push Notifications', 'Chart Libraries', 'Firebase'],
                'features': ['Habit creation and tracking', 'Streak counters', 'Progress charts', 'Reminder notifications', 'Social sharing'],
                'objectives': ['Learn mobile development patterns', 'Implement local storage', 'Handle push notifications', 'Build engaging user interfaces']
            },
            {
                'title': 'Augmented Reality Plant Identifier',
                'description': 'Create an AR mobile app that identifies plants using camera input, provides care instructions, and tracks plant collections.',
                'technologies': ['Flutter', 'ARCore/ARKit', 'TensorFlow Lite', 'Plant API', 'SQLite'],
                'features': ['Camera-based plant identification', 'AR overlay information', 'Care reminders', 'Plant collection tracker', 'Offline mode'],
                'objectives': ['Learn AR development', 'Implement machine learning on mobile', 'Build camera functionality', 'Handle offline data sync']
            },
            {
                'title': 'Fitness Challenge App',
                'description': 'Develop a social fitness app where users can create challenges, track workouts, compete with friends, and share achievements.',
                'technologies': ['Swift/Kotlin', 'HealthKit/Google Fit', 'Firebase', 'Push Notifications', 'Social APIs'],
                'features': ['Workout tracking', 'Social challenges', 'Leaderboards', 'Progress sharing', 'Achievement system'],
                'objectives': ['Integrate health APIs', 'Build social features', 'Implement real-time updates', 'Create gamification systems']
            }
        ],
        "Machine Learning & AI": [
            {
                'title': 'Image Classification Web Service',
                'description': 'Build a web service that classifies images using deep learning, with model training, API endpoints, and a user-friendly interface.',
                'technologies': ['Python', 'TensorFlow', 'FastAPI', 'Docker', 'AWS/GCP', 'React'],
                'features': ['Custom model training', 'REST API endpoints', 'Batch processing', 'Model versioning', 'Performance monitoring'],
                'objectives': ['Learn deep learning frameworks', 'Build ML APIs', 'Deploy ML models', 'Handle model lifecycle']
            },
            {
                'title': 'Chatbot with Natural Language Understanding',
                'description': 'Create an intelligent chatbot that understands context, handles multiple intents, and provides personalized responses.',
                'technologies': ['Python', 'spaCy', 'Rasa', 'PostgreSQL', 'WebSocket', 'Docker'],
                'features': ['Intent recognition', 'Context awareness', 'Multi-turn conversations', 'Personalization', 'Analytics dashboard'],
                'objectives': ['Learn NLP fundamentals', 'Build conversational AI', 'Implement context management', 'Create training pipelines']
            }
        ],
        "Game Development": [
            {
                'title': '2D Platformer Game',
                'description': 'Develop a complete 2D platformer game with levels, enemies, power-ups, and a level editor using modern game development tools.',
                'technologies': ['Unity', 'C#', 'Tilemap System', 'Animation System', 'Audio System'],
                'features': ['Character movement and physics', 'Enemy AI systems', 'Level progression', 'Power-up system', 'Level editor'],
                'objectives': ['Learn game physics', 'Implement AI behaviors', 'Create game mechanics', 'Build user interfaces']
            },
            {
                'title': 'Multiplayer Card Game',
                'description': 'Build a real-time multiplayer card game with matchmaking, turn-based gameplay, and spectator mode.',
                'technologies': ['Godot', 'WebSocket', 'Node.js', 'MongoDB', 'Game Networking'],
                'features': ['Real-time multiplayer', 'Matchmaking system', 'Turn-based mechanics', 'Spectator mode', 'Replay system'],
                'objectives': ['Learn network programming', 'Implement game state management', 'Build matchmaking logic', 'Handle real-time synchronization']
            }
        ]
    }
    
    # Get projects for the focus area, with fallback to programming
    available_projects = project_pool.get(focus_area, project_pool["Programming & Software Development"])
    
    # If we need more projects than available, include from other categories
    selected_projects = []
    if num_projects <= len(available_projects):
        selected_projects = available_projects[:num_projects]
    else:
        selected_projects.extend(available_projects)
        # Add projects from other categories to reach the requested number
        remaining_needed = num_projects - len(available_projects)
        all_other_projects = []
        for category, projects in project_pool.items():
            if category != focus_area:
                all_other_projects.extend(projects)
        selected_projects.extend(all_other_projects[:remaining_needed])
    
    # Finalize projects with timeline and difficulty
    final_projects = []
    for project in selected_projects:
        final_project = project.copy()
        final_project.update({
            'timeline': timeline,
            'difficulty': difficulty_level,
            'resources': [
                f"{project['technologies'][0]} Official Documentation",
                f"GitHub repositories for {project['title'].lower().replace(' ', '-')}",
                f"YouTube tutorials on {project['technologies'][1] if len(project['technologies']) > 1 else project['technologies'][0]}",
                "Stack Overflow community",
                "Medium articles and tech blogs"
            ]
        })
        final_projects.append(final_project)
    
    return final_projects

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
