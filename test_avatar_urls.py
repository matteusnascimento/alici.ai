import requests
from urllib.parse import urlparse

def test_url_accessibility(url):
    """Test if a URL is accessible and returns a successful response"""
    try:
        response = requests.head(url, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing {url}: {str(e)}")
        return False

def main():
    # URLs usadas no código Flask
    urls = [
        "https://static-us-img.skywork.ai/prod/analysis/2026-01-12/3193088764620888317/2010863530756530176_f8987f49506aafd4b7bcbb25d6126a2b.jpg",
        "https://static-us-img.skywork.ai/prod/analysis/2026-01-12/3193088764620888317/2010826893896966144_9ab19eaf914ff4a0bf4d584cf3022105.jpg"
    ]
    
    print("🧪 Testando acessibilidade das URLs do avatar...\n")
    
    for i, url in enumerate(urls, 1):
        print(f"Testando URL {i}:")
        print(f"  {url}")
        
        if test_url_accessibility(url):
            print("  ✅ URL acessível\n")
        else:
            print("  ❌ URL inacessível\n")

if __name__ == "__main__":
    main()