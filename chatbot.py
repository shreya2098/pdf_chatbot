from flask import Blueprint, request, jsonify
from function import *
# Create a Blueprint for the API
api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok', 'message': 'Service is running'}), 200

@api_blueprint.route('/upload', methods=['POST'])
def upload_pdfs():
    """Endpoint to upload PDFs and initialize the chatbot."""
    pdf_files = request.files.getlist('pdf_files')

    if not pdf_files:
        return jsonify({'error': 'No PDF files provided'}), 400

    pdf_docs = [BytesIO(pdf.read()) for pdf in pdf_files]

    # Process PDFs
    raw_text = get_pdf_text(pdf_docs)
    if not raw_text:
        return jsonify({'error': 'No text extracted from the PDFs'}), 400

    text_chunks = get_text_chunks(raw_text)
    vectorstore = get_vectorstore(text_chunks)

    # Create conversation chain
    conversation_id = request.form.get('conversation_id', 'default')
    conversation_chains[conversation_id] = get_conversation_chain(vectorstore)

    return jsonify({'message': 'PDFs processed and chatbot initialized', 'conversation_id': conversation_id})

@api_blueprint.route('/chat', methods=['POST'])
def chat():
    """Endpoint for chatting with the initialized chatbot."""
    # Expecting form data
    conversation_id = request.form.get('conversation_id', 'default')
    user_question = request.form.get('question')

    # Check if the conversation exists
    if conversation_id not in conversation_chains:
        return jsonify({'error': 'Conversation not found'}), 400

    # Check if the question is provided
    if not user_question:
        return jsonify({'error': 'No question provided'}), 400

    # Get the conversation chain for the conversation_id
    conversation_chain = conversation_chains[conversation_id]
    
    # Generate a response from the chatbot
    response = conversation_chain({'question': user_question})

    # Retrieve chat history for the response
    chat_history = response['chat_history']
    response_message = chat_history[-1].content  # Get the last message (bot's response)

    # Return the response message
    return jsonify({'response': response_message})
