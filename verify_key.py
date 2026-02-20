import google.generativeai as genai

def test_api_key(api_key):
    print(f"Testing API Key: {api_key[:8]}...")
    try:
        genai.configure(api_key=api_key)
        # Use a confirmed model name from the list
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content("Reply with 'API_KEY_WORKS'")
        
        if "API_KEY_WORKS" in response.text:
            print("✅ SUCCESS: The API key is valid and working!")
        else:
            print(f"⚠️ UNEXPECTED RESPONSE: {response.text}")
            
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")

if __name__ == "__main__":
    key = "AIzaSyAEei7cGiX8sRARaLwUjG76V4JtKzsnrBg"
    test_api_key(key)
