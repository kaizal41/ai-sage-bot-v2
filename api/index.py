def call_gemini_api(prompt):
    # Model name ကို gemini-1.5-flash-latest လို့ အတိအကျ ပြောင်းလိုက်ပါတယ်
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            # ဘာကြောင့် Error တက်လဲဆိုတာ အသေးစိတ် ပြန်ပို့ပေးမယ်
            return f"Gemini Error ({response.status_code}): {response.text}"
    except Exception as e:
        return f"Request Error: {str(e)}"
