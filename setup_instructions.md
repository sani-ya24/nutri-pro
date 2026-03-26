# NutriPro Backend Setup Instructions

## Prerequisites

1. **Python 3.8 or higher** installed on your system
2. **Gemini API Key** from Google AI Studio

## Setup Steps

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Your Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the API key

### 3. Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and replace `your-gemini-api-key-here` with your actual Gemini API key:
   ```
   GEMINI_API_KEY=your-actual-api-key-here
   ```

### 4. Run the Backend Server

```bash
python backend.py
```

The server will start on `http://localhost:5000`

### 5. Open the Frontend

Open `index.html` in your web browser. The frontend will automatically connect to the backend.

## Features Implemented

### Backend Features:
- ✅ User registration and login with bcrypt password hashing
- ✅ JSON file-based data storage (users.json, profiles.json, chat_history.json)
- ✅ Gemini AI integration for intelligent chatbot responses
- ✅ User profile management (age, weight, height, water intake, etc.)
- ✅ Chat history storage and retrieval
- ✅ CORS enabled for frontend communication

### Frontend Integration:
- ✅ Login form connected to backend authentication
- ✅ Chatbot messages sent to Gemini AI via backend
- ✅ Profile data synchronized with backend
- ✅ Water intake tracking saved to backend
- ✅ Real-time chat with personalized responses based on user profile

## API Endpoints

- `POST /api/register` - Register new user
- `POST /api/login` - User authentication
- `GET /api/profile/<user_id>` - Get user profile
- `PUT /api/profile/<user_id>` - Update user profile
- `POST /api/chat` - Send message to chatbot
- `GET /api/chat/history/<user_id>` - Get chat history
- `GET /api/health` - Health check

## Data Storage Structure

### users.json
```json
{
  "user@example.com": {
    "id": "uuid",
    "email": "user@example.com",
    "password": "hashed_password",
    "name": "User Name",
    "created_at": "2024-01-01T00:00:00"
  }
}
```

### profiles.json
```json
{
  "user_id": {
    "name": "User Name",
    "age": 25,
    "weight": 70,
    "height": 170,
    "water_intake": 3,
    "goal_progress": 65,
    "diet_goal": "Weight Management"
  }
}
```

### chat_history.json
```json
{
  "user_id": [
    {
      "user_message": "Hello",
      "bot_response": "Hi there! How can I help you today?",
      "timestamp": "2024-01-01T00:00:00"
    }
  ]
}
```

## Security Notes

⚠️ **Important**: This implementation uses JSON files for data storage, which is suitable for development and small-scale applications but has limitations:

- No concurrent access protection
- Limited scalability
- Basic security measures
- Not recommended for production use

For production applications, consider using a proper database like PostgreSQL with Supabase.

## Troubleshooting

1. **"Module not found" errors**: Make sure you've installed all dependencies with `pip install -r requirements.txt`

2. **Gemini API errors**: Verify your API key is correct and you have sufficient quota

3. **CORS errors**: Make sure the backend server is running on port 5000

4. **Login issues**: Check the browser console for error messages and verify the backend is responding

## Testing the Application

1. Start the backend server
2. Open `index.html` in your browser
3. Try registering a new user
4. Log in with your credentials
5. Test the chatbot functionality
6. Update your profile information
7. Track water intake

The chatbot will provide personalized responses based on your profile data and use Gemini AI for intelligent conversations about nutrition and health.