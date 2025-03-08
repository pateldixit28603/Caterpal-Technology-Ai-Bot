import os
import openai
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Retrieve OpenAI API key securely
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Error: Missing OpenAI API Key. Please set it in a .env file.")

# Set OpenAI API key
openai.api_key = api_key

# In-memory session store
user_sessions = {}

def get_persona():
    """
    Returns a system message that sets the chatbot's persona
    and conversation strategy to gather event details, propose
    a menu with pricing, and confirm booking.
    Also instructs the bot to present meal options in a 
    structured format to prevent text overflow.
    """
    return {
        "role": "system",
        "content": (
            "You are CaterPal Assistant, a sophisticated AI specialized in catering services. "
            "Your primary goal is to help users plan their catering events by asking relevant questions and "
            "offering suitable menu suggestions with pricing.\n\n"

            "When proposing meal options, please present them in a clear, structured format using headings and bullet points. "
            "For example:\n\n"
            "**Option 1:**\n"
            "- [Item 1]\n"
            "- [Item 2]\n"
            "*Approx. Price:* $XXX\n\n"
            "**Option 2:**\n"
            "- [Item 1]\n"
            "- [Item 2]\n"
            "*Approx. Price:* $YYY\n\n"

            "### Interaction Flow:\n"
            "1. Greet the user politely and determine the type of event (e.g., wedding, birthday, corporate lunch, etc.).\n"
            "2. Ask for the event date and time (or approximate timing).\n"
            "3. Ask for the expected number of guests.\n"
            "4. Inquire about any dietary preferences or restrictions.\n"
            "5. Based on these details, propose recommended menu options (structured as above) along with approximate pricing.\n"
            "6. Ask for the event location/address and any other relevant details (like contact info).\n"
            "7. Summarize all the details (date, time, guest count, dietary needs, chosen menu, total price, address, etc.) "
            "   and confirm with the user if they wish to finalize or make changes.\n"
            "8. Maintain a friendly, professional, and concise tone.\n\n"
            "If the user confirms a particular option, finalize it. If they need changes, adapt accordingly."
        )
    }

@app.route("/")
def index():
    """Render the homepage."""
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    """Handles chat messages and generates AI responses."""
    data = request.get_json()
    user_id = data.get("user_id")
    user_message = data.get("message")

    if not user_id or not user_message:
        return jsonify({"error": "user_id and message are required"}), 400

    # If new user, initialize conversation list
    if user_id not in user_sessions:
        user_sessions[user_id] = []

    # Append user's message
    user_sessions[user_id].append({"role": "user", "content": user_message})
    
    # Build conversation with system instructions
    conversation = [get_persona()] + user_sessions[user_id]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation,
            max_tokens=512,
            temperature=0.7
        )
        assistant_message = response["choices"][0]["message"]["content"]
        
        # Append assistant response
        user_sessions[user_id].append({"role": "assistant", "content": assistant_message})
        
        return jsonify({"assistant": assistant_message}), 200
    except openai.error.OpenAIError as e:
        return jsonify({"error": f"OpenAI API error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

@app.route("/clear_session", methods=["POST"])
def clear_session():
    """Clears the chat session for a specific user."""
    data = request.get_json()
    user_id = data.get("user_id")
    
    if user_id in user_sessions:
        user_sessions[user_id] = []
        return jsonify({"message": "Session cleared successfully"}), 200
    else:
        return jsonify({"message": "User session not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
