from flask import Flask
from dotenv import load_dotenv
from chatbot import api_blueprint

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Register the API blueprint with the Flask app
app.register_blueprint(api_blueprint, url_prefix='/api')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
