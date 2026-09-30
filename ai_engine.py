import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Initialize the Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def extract_transaction_data(model_name: str, merchant_message: str) -> dict:
    """
    Takes a raw text message and extracts structured database fields using the specified model.
    """
    system_prompt = """
    You are KioskLedger's core data extraction AI. 
    Your job is to read unstructured sales messages from informal merchants and extract the data into a STRICT JSON object.
    
    The transaction_type must be exactly one of: ["CASH", "CREDIT", "REPAYMENT"].
    - If they sell on credit or someone owes them, it's CREDIT.
    - If someone is paying back an old debt, it's REPAYMENT.
    - Otherwise, it's CASH.
    
    Respond ONLY with a valid JSON object matching this exact structure:
    {
        "customer_name": "Name or null if unknown",
        "items_summary": [{"item_name": "Rice", "qty": 1}],
        "total_amount": 5000.0,
        "transaction_type": "CASH"
    }
    """

    try:
        response = client.chat.completions.create(
            model=model_name,  # Dynamically passed from the router
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": merchant_message}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        
        ai_output = response.choices[0].message.content
        return json.loads(ai_output)
        
    except Exception as e:
        print(f"AI Extraction Error: {e}")
        return None


def transcribe_audio(model_name: str, audio_file_path: str) -> str:
    """
    Placeholder: Will route WhatsApp voice notes to Whisper for transcription.
    """
    print(f"🎙️ Routing to audio model: {model_name}...")
    # Logic to open audio file and transcribe will go here
    return "Transcribed audio text placeholder"


def route_and_process(payload_type: str, raw_data):
    """
    The central API routing gateway. 
    Dynamically assigns tasks to specialized Groq models based on the payload type.
    """
    if payload_type == "audio":
        # Route to Speech-to-Text for voice notes
        model_name = "whisper-large-v3"
        transcribed_text = transcribe_audio(model_name, raw_data)
        # Chain the transcribed text directly into the text extractor
        return extract_transaction_data("openai/gpt-oss-20b", transcribed_text)

    elif payload_type == "text":
        # Route to a fast, stable model for JSON extraction
        model_name = "openai/gpt-oss-120b" 
        print(f"🧠 Routing to text model: {model_name}...")
        return extract_transaction_data(model_name, raw_data)

    elif payload_type == "image":
        # Route to Vision model for receipt scanning
        model_name = "qwen-3.8-27b"
        print(f"👁️ Routing to vision model: {model_name}...")
        return {"status": "Image processing to be implemented"}

    else:
        raise ValueError("Unsupported payload type")