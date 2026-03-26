from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import bcrypt
import google.generativeai as genai
from datetime import datetime
import uuid
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure Gemini AI
# You'll need to set your API key as an environment variable or replace this with your actual key
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'your-gemini-api-key-here')
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Gemini model
model = genai.GenerativeModel('gemini-2.0-flash-lite')

# Data file paths
USERS_FILE = 'data/users.json'
PROFILES_FILE = 'data/profiles.json'
CHAT_HISTORY_FILE = 'data/chat_history.json'

def ensure_data_directory():
    """Create data directory and initialize JSON files if they don't exist"""
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Initialize users.json
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump({}, f)
    
    # Initialize profiles.json
    if not os.path.exists(PROFILES_FILE):
        with open(PROFILES_FILE, 'w') as f:
            json.dump({}, f)
    
    # Initialize chat_history.json
    if not os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, 'w') as f:
            json.dump({}, f)

def load_json_file(filepath):
    """Load data from JSON file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_json_file(filepath, data):
    """Save data to JSON file"""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        email = data.get('email', '').lower().strip()
        password = data.get('password', '')
        name = data.get('name', '')
        
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password are required'}), 400
        
        users = load_json_file(USERS_FILE)
        
        # Check if user already exists
        if email in users:
            return jsonify({'success': False, 'message': 'User already exists'}), 400
        
        # Create new user
        user_id = str(uuid.uuid4())
        users[email] = {
            'id': user_id,
            'email': email,
            'password': hash_password(password),
            'name': name,
            'created_at': datetime.now().isoformat()
        }
        
        save_json_file(USERS_FILE, users)
        
        # Create default profile
        profiles = load_json_file(PROFILES_FILE)
        profiles[user_id] = {
            'name': name or 'User',
            'age': 25,
            'weight': 70,
            'height': 170,
            'water_intake': 0,
            'goal_progress': 0,
            'diet_goal': 'Weight Management'
        }
        save_json_file(PROFILES_FILE, profiles)
        
        return jsonify({
            'success': True, 
            'message': 'User registered successfully',
            'user_id': user_id
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Authenticate user login"""
    try:
        data = request.get_json()
        email = data.get('email', '').lower().strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password are required'}), 400
        
        users = load_json_file(USERS_FILE)
        
        # Check if user exists
        if email not in users:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
        
        user = users[email]
        
        # Verify password
        if not verify_password(password, user['password']):
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user_id': user['id'],
            'name': user['name']
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/profile/<user_id>', methods=['GET'])
def get_profile(user_id):
    """Get user profile data"""
    try:
        profiles = load_json_file(PROFILES_FILE)
        
        if user_id not in profiles:
            return jsonify({'success': False, 'message': 'Profile not found'}), 404
        
        return jsonify({
            'success': True,
            'profile': profiles[user_id]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/profile/<user_id>', methods=['PUT'])
def update_profile(user_id):
    """Update user profile data"""
    try:
        data = request.get_json()
        profiles = load_json_file(PROFILES_FILE)
        
        if user_id not in profiles:
            return jsonify({'success': False, 'message': 'Profile not found'}), 404
        
        # Update profile fields
        profile = profiles[user_id]
        for key, value in data.items():
            if key in ['name', 'age', 'weight', 'height', 'water_intake', 'goal_progress', 'diet_goal']:
                profile[key] = value
        
        profiles[user_id] = profile
        save_json_file(PROFILES_FILE, profiles)
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'profile': profile
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat_with_gemini():
    """Handle chat messages with Gemini AI"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        user_id = data.get('user_id', 'anonymous')
        
        if not user_message:
            return jsonify({'success': False, 'message': 'Message is required'}), 400
        
        # Get user profile for context
        profiles = load_json_file(PROFILES_FILE)
        user_profile = profiles.get(user_id, {})
        
        # Create context-aware prompt for nutrition assistant
        context_prompt = f"""
        You are NutriBot, a friendly and knowledgeable nutrition assistant. You help users with:
        - Personalized nutrition advice
        - Meal planning and recipes
        - Calorie tracking and diet goals
        - Healthy lifestyle tips
        - Water intake reminders
        - BMI and health assessments
        
        User Profile Context:
        - Name: {user_profile.get('name', 'User')}
        - Age: {user_profile.get('age', 'Not specified')}
        - Weight: {user_profile.get('weight', 'Not specified')} kg
        - Height: {user_profile.get('height', 'Not specified')} cm
        - Diet Goal: {user_profile.get('diet_goal', 'Not specified')}
        
        User Message: {user_message}
        
        Please provide a helpful, encouraging, and personalized response. Keep it conversational and include relevant emojis. If the user asks about topics outside nutrition and health, politely redirect them back to health-related topics.
        """
        
        # Generate response using Gemini
        response = model.generate_content(context_prompt)
        bot_response = response.text
        
        # Save chat history
        chat_history = load_json_file(CHAT_HISTORY_FILE)
        if user_id not in chat_history:
            chat_history[user_id] = []
        
        chat_history[user_id].append({
            'user_message': user_message,
            'bot_response': bot_response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 50 messages per user to prevent file from growing too large
        if len(chat_history[user_id]) > 50:
            chat_history[user_id] = chat_history[user_id][-50:]
        
        save_json_file(CHAT_HISTORY_FILE, chat_history)
        
        return jsonify({
            'success': True,
            'response': bot_response
        })
        
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        # Fallback response if Gemini fails
        fallback_responses = {
            'diet plan': "Here's a personalized diet plan for you: 🥗\n\n🌅 Breakfast: Greek yogurt with berries\n☀️ Lunch: Quinoa salad with vegetables\n🌙 Dinner: Grilled fish with steamed broccoli\n\nWould you like me to adjust this based on your preferences?",
            'calories': "I'd be happy to help you track your calories! 📊 Could you tell me what you've eaten today so I can help calculate your intake?",
            'water': "💧 Great question about hydration! I recommend drinking 8 glasses of water daily. Would you like me to help you set up reminders?",
            'recipe': "🍎 I'd love to share some healthy recipes with you! What type of meal are you looking for - breakfast, lunch, or dinner?",
            'default': "I'm here to help with your nutrition and health goals! 🌟 You can ask me about meal planning, calorie tracking, healthy recipes, or any other nutrition-related questions."
        }
        
        user_message_lower = user_message.lower()
        response_key = 'default'
        for key in fallback_responses:
            if key in user_message_lower:
                response_key = key
                break
        
        return jsonify({
            'success': True,
            'response': fallback_responses[response_key]
        })

@app.route('/api/chat/history/<user_id>', methods=['GET'])
def get_chat_history(user_id):
    """Get chat history for a user"""
    try:
        chat_history = load_json_file(CHAT_HISTORY_FILE)
        user_history = chat_history.get(user_id, [])
        
        return jsonify({
            'success': True,
            'history': user_history
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'NutriPro Backend is running!',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    ensure_data_directory()
    print("🥗 NutriPro Backend starting...")
    print("📁 Data directory initialized")
    print("🤖 Gemini AI configured")
    print("🚀 Server running on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)