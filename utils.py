import requests, json

def fetch(url):
    for _ in range(3):
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 200 and r.text.strip():
                return r.text
        except Exception:
            pass
    return None