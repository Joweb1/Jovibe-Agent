import google.generativeai as genai

def list_models(api_key):
    try:
        genai.configure(api_key=api_key)
        print("Available models:")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_models("AIzaSyAEei7cGiX8sRARaLwUjG76V4JtKzsnrBg")
