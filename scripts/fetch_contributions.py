import requests
import json
import os

USERNAME = "syedhassanstudies-rgb"

def fetch_contributions():
    os.makedirs('data', exist_ok=True)
    # Using reliable Deno mirror
    url = f"https://github-contributions-api.deno.dev/https://github.com/{USERNAME}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            with open('data/contributions.json', 'w') as f:
                json.dump(data, f, indent=2)
            print("data/contributions.json updated successfully.")
            return
    except Exception as e:
        print(f"Network error fetching contributions: {e}")

    # Fallback to prevent JSONDecodeError if network fails
    if not os.path.exists('data/contributions.json') or os.path.getsize('data/contributions.json') == 0:
        with open('data/contributions.json', 'w') as f:
            json.dump({"contributions": []}, f)
        print("Created empty fallback data/contributions.json.")

if __name__ == "__main__":
    fetch_contributions()