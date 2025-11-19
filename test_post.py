"""
Test script to post a sample blog to your server without using the AI API
"""
import requests
from datetime import datetime

# Sample blog content
title = "Test Blog Post: What is AI?"
content = """# What is AI?

Artificial Intelligence (AI) is transforming our world in remarkable ways. This technology enables machines to perform tasks that typically require human intelligence.

## Understanding AI

AI encompasses various technologies including:
- Machine Learning
- Natural Language Processing
- Computer Vision
- Robotics

## Applications of AI

AI is being used in:
1. Healthcare diagnostics
2. Autonomous vehicles
3. Virtual assistants
4. Content recommendations

## Conclusion

AI continues to evolve and shape our future in exciting ways!
"""

topic = "What is AI?"
timestamp = datetime.now().isoformat()

# Post to your server
endpoint = "http://127.0.0.1:5500/blogs"

print(f"📤 Posting test blog to {endpoint}...")

try:
    response = requests.post(
        endpoint,
        json={
            "title": title,
            "content": content,
            "topic": topic,
            "timestamp": timestamp
        },
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code in [200, 201]:
        print(f"✅ Success! Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        print(f"\n🌐 View your blog at: http://127.0.0.1:5500")
    else:
        print(f"❌ Failed! Status: {response.status_code}")
        print(f"   Error: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n💡 Make sure your server is running:")
    print("   python server.py")
