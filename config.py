import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://user:password@localhost/binmaqsood'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # WhatsApp API configuration (Meta Cloud API / Twilio style)
    WHATSAPP_API_URL = os.environ.get('WHATSAPP_API_URL', 'https://graph.facebook.com/v18.0/PHONE_NUMBER_ID/messages')
    WHATSAPP_ACCESS_TOKEN = os.environ.get('WHATSAPP_ACCESS_TOKEN', 'your_access_token')
    WHATSAPP_OWNER_NUMBER = os.environ.get('WHATSAPP_OWNER_NUMBER', '+923080320007')  # Owner's number
    # Sender phone number ID (provided by Meta)
    WHATSAPP_FROM_PHONE_NUMBER_ID = os.environ.get('WHATSAPP_FROM_PHONE_NUMBER_ID', 'your_phone_number_id')

    # File upload settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
    INVOICE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'invoices')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    # Company details for invoice
    COMPANY_NAME = "Bin Maqsood"
    COMPANY_EMAIL = "binmaqsoodtextilefsd@gmail.com"
    COMPANY_ADDRESS = "Factory Area, 38000, Pakistan"