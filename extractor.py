import pypdf
import io

def extract_text_from_pdf(uploaded_file):
    """
    PDF file se text extract karta hai
    Returns: (text, page_count, char_count) tuple
    """
    try:
        pdf_reader = pypdf.PdfReader(io.BytesIO(uploaded_file.read()))
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        if not text.strip():
            return None, 0, 0
            
        return text, len(pdf_reader.pages), len(text)
    
    except Exception as e:
        raise Exception(f"PDF read karne mein error: {str(e)}")


def validate_circular_text(text):
    """
    Check karta hai ki text regulatory circular jaisa lagta hai ya nahi
    Returns: (is_valid, message) tuple
    """
    if not text or len(text.strip()) < 100:
        return False, "Text bahut chhota hai - valid circular nahi lagta"
    
    # Common RBI/SEBI keywords
    keywords = [
        "circular", "rbi", "sebi", "reserve bank", "securities",
        "compliance", "bank", "regulation", "guidelines", "directions",
        "master", "notification", "amendment"
    ]
    
    text_lower = text.lower()
    found = [kw for kw in keywords if kw in text_lower]
    
    if len(found) == 0:
        return False, "⚠️ Warning: Ye regulatory circular nahi lagta - phir bhi try kar sakte ho"
    
    return True, f"✅ Valid circular detected - keywords found: {', '.join(found[:3])}"