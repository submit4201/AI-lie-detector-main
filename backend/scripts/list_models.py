import os
import sys
import json
from urllib import request, error

# Try to read key from environment first, then .env
key = os.environ.get('GEMINI_API_KEY')
if not key:
    # Try to read from .env in repo root
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith('GEMINI_API_KEY'):
                    parts = line.strip().split('=', 1)
                    if len(parts) == 2:
                        key = parts[1].strip().strip('"').strip("'")
                        break
    except FileNotFoundError:
        pass

if not key:
    print('No GEMINI_API_KEY found in environment or .env')
    sys.exit(2)

url = f'https://generativelanguage.googleapis.com/v1beta/models?key={key}'

try:
    with request.urlopen(url, timeout=15) as resp:
        data = json.load(resp)
        models = []
        for m in data.get('models', []):
            name = m.get('name') or m.get('model') or m.get('id')
            if name:
                models.append(name.split('/')[-1])
        if models:
            print('Available models:')
            for md in models:
                print('-', md)
        else:
            print('No models returned by API (empty list). Full response:')
            print(json.dumps(data)[:2000])
except error.HTTPError as e:
    try:
        body = e.read().decode('utf-8')
    except Exception:
        body = ''
    print(f'HTTPError {e.code}: {body[:2000]}')
    sys.exit(3)
except Exception as e:
    print('Error calling ListModels:', str(e))
    sys.exit(4)
