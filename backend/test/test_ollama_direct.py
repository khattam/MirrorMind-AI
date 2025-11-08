import requests

def test_ollama_api():
    # Get API key from environment variable
    import os
    api_key = os.getenv("OLLAMA_API_KEY")
    
    if not api_key:
        print("❌ OLLAMA_API_KEY environment variable not set")
        return False
    
    print(f'API Key (first 20 chars): {api_key[:20]}...')
    
    try:
        print('🔄 Testing Ollama cloud API...')
        response = requests.post(
            'https://ollama.com/api/generate',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            },
            json={
                'model': 'gpt-oss:20b-cloud',
                'prompt': 'Hello, respond with just "API test successful"',
                'stream': False
            },
            timeout=30
        )
        
        print(f'Status Code: {response.status_code}')
        
        if response.status_code == 200:
            result = response.json()
            print('✅ SUCCESS! API is working')
            print(f'Model Response: {result.get("response", "No response field")}')
            return True
        else:
            print(f'❌ Error {response.status_code}: {response.text}')
            return False
            
    except requests.exceptions.Timeout:
        print('❌ Request timed out - API might be slow')
        return False
    except requests.exceptions.RequestException as e:
        print(f'❌ Request Exception: {e}')
        return False
    except Exception as e:
        print(f'❌ Unexpected Exception: {e}')
        return False

if __name__ == "__main__":
    test_ollama_api()