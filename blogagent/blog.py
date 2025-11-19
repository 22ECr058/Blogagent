# blogagent.py - Blog Agent with Environment Variables
import os
import sys
import requests
import httpx
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load API keys from environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MEDIUM_API_KEY = os.getenv("MEDIUM_API_KEY", "")
DEVTO_API_KEY = os.getenv("DEVTO_API_KEY", "")
ENDPOINT_URL = os.getenv("BLOG_ENDPOINT_URL", "")  # Custom endpoint for posting

if not GOOGLE_API_KEY:
    print("ERROR: GOOGLE_API_KEY environment variable not set!")
    print("Set it with: $env:GOOGLE_API_KEY='your_api_key_here'")
    exit()

print("Gemini API Key LOADED SUCCESSFULLY!")
print("Blog Agent is READY!\n")

# GEMINI 2.0 FLASH with timeout settings
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.7,
    max_tokens=8192,
    timeout=60,  # 60 second timeout
    max_retries=2  # Retry up to 2 times
)

# Create prompt template for blog writing
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a world-class SEO blog writer. Write a 1500+ word blog post in Markdown format with:
- Catchy H1 title
- Meta description (150 chars)
- H2/H3 structure with clear sections
- Bullet points and numbered lists
- Include relevant examples and case studies
- Strong call-to-action at the end
- Professional, friendly, and engaging tone

Format the output as clean Markdown that's ready to publish."""),
    ("human", "Write a comprehensive SEO-optimized blog post about: {topic}")
])

# Create the chain using LCEL (LangChain Expression Language)
chain = prompt | llm | StrOutputParser()

def publish_to_medium(title: str, content: str) -> bool:
    """Publish blog post to Medium"""
    if not MEDIUM_API_KEY:
        return False
    
    try:
        # Get user ID
        headers = {"Authorization": f"Bearer {MEDIUM_API_KEY}"}
        user_resp = requests.get("https://api.medium.com/v1/me", headers=headers)
        user_id = user_resp.json()["data"]["id"]
        
        # Publish post
        post_data = {
            "title": title,
            "contentFormat": "markdown",
            "content": content,
            "publishStatus": "draft"  # Change to "public" for immediate publish
        }
        resp = requests.post(
            f"https://api.medium.com/v1/users/{user_id}/posts",
            headers=headers,
            json=post_data
        )
        
        if resp.status_code == 201:
            url = resp.json()["data"]["url"]
            print(f"  ✅ Medium: {url}")
            return True
    except Exception as e:
        print(f"  ❌ Medium failed: {e}")
    return False

def publish_to_devto(title: str, content: str) -> bool:
    """Publish blog post to Dev.to"""
    if not DEVTO_API_KEY:
        return False
    
    try:
        headers = {
            "api-key": DEVTO_API_KEY,
            "Content-Type": "application/json"
        }
        post_data = {
            "article": {
                "title": title,
                "body_markdown": content,
                "published": False  # Change to True for immediate publish
            }
        }
        resp = requests.post(
            "https://dev.to/api/articles",
            headers=headers,
            json=post_data
        )
        
        if resp.status_code == 201:
            url = resp.json()["url"]
            print(f"  ✅ Dev.to: {url}")
            return True
    except Exception as e:
        print(f"  ❌ Dev.to failed: {e}")
    return False

def publish_to_endpoint(title: str, content: str, topic: str) -> bool:
    """Publish blog post to custom endpoint"""
    if not ENDPOINT_URL:
        return False
    
    try:
        headers = {"Content-Type": "application/json"}
        post_data = {
            "title": title,
            "content": content,
            "topic": topic,
            "timestamp": datetime.now().isoformat()
        }
        resp = requests.post(ENDPOINT_URL, headers=headers, json=post_data)
        
        if resp.status_code in [200, 201]:
            print(f"  ✅ Custom Endpoint: {ENDPOINT_URL}")
            print(f"     Response: {resp.json() if resp.text else 'Success'}")
            return True
        else:
            print(f"  ❌ Endpoint failed with status {resp.status_code}: {resp.text}")
            return False
    except Exception as e:
        print(f"  ❌ Endpoint failed: {e}")
    return False

def extract_title(content: str) -> str:
    """Extract title from markdown content"""
    lines = content.strip().split('\n')
    for line in lines:
        if line.startswith('# '):
            return line[2:].strip()
    return "Untitled Blog Post"

def run():
    # Get topic from command line argument or prompt user
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:]).strip()
    else:
        topic = input("Enter blog topic: ").strip()
    
    if not topic:
        topic = "How to Make $10,000/Month with AI in 2025"
    
    print(f"\n🚀 Generating blog post about: {topic}...")
    print("⏳ This may take 30-60 seconds for a full blog post...\n")
    
    # Generate the blog using the chain with error handling
    try:
        content = chain.invoke({"topic": topic})
    except httpx.TimeoutException:
        print("\n❌ ERROR: Request timed out after 60 seconds")
        print("   The Google API is taking too long to respond.")
        print("   This could mean:")
        print("   - Google's servers are experiencing high load")
        print("   - Your internet connection is slow")
        print("   - The API quota may be exhausted")
        print("\n   Solutions:")
        print("   - Wait a few minutes and try again")
        print("   - Check your internet connection")
        print("   - Verify your API quota at https://aistudio.google.com/")
        exit(1)
    except httpx.ConnectError as e:
        print("\n❌ ERROR: Cannot connect to Google API")
        print(f"   {e}")
        print("\n   Solutions:")
        print("   - Check your internet connection")
        print("   - Verify Google services are accessible in your region")
        print("   - Try again in a few minutes")
        exit(1)
    except Exception as e:
        error_msg = str(e)
        if '429' in error_msg:
            print("\n❌ ERROR: API quota exceeded")
            print("   You've hit the daily limit of 250 requests.")
            print("   Wait for quota reset (UTC midnight) or use a different API key.")
        elif 'timeout' in error_msg.lower():
            print("\n❌ ERROR: Request timed out")
            print("   Google API is taking too long. Try again in a few minutes.")
        elif '503' in error_msg or 'connect' in error_msg.lower():
            print("\n❌ ERROR: Google API temporarily unavailable")
            print("   The service is experiencing issues. Try again later.")
        else:
            print(f"\n❌ ERROR: {e}")
        exit(1)
    
    # Extract title from content
    title = extract_title(content)
    
    print("="*70)
    print(f"✅ BLOG GENERATED!")
    print("="*70)
    print(f"\n📄 Title: {title}")
    print(f"📊 Length: {len(content)} characters, ~{len(content.split())} words")
    
    # Post directly to endpoint
    if not ENDPOINT_URL:
        print("\n❌ ERROR: No endpoint URL configured!")
        print("   Set it with: $env:BLOG_ENDPOINT_URL='https://your-api.com/posts'")
        exit(1)
    
    print(f"\n📤 Posting to endpoint: {ENDPOINT_URL}...")
    
    try:
        headers = {"Content-Type": "application/json"}
        post_data = {
            "title": title,
            "content": content,
            "topic": topic,
            "timestamp": datetime.now().isoformat()
        }
        resp = requests.post(ENDPOINT_URL, headers=headers, json=post_data, timeout=30)
        
        if resp.status_code in [200, 201]:
            print(f"✅ Successfully posted to endpoint!")
            print(f"   Status: {resp.status_code}")
            if resp.text:
                try:
                    print(f"   Response: {resp.json()}")
                except:
                    print(f"   Response: {resp.text[:200]}")
        else:
            print(f"❌ Failed to post to endpoint")
            print(f"   Status: {resp.status_code}")
            print(f"   Error: {resp.text}")
            exit(1)
    except Exception as e:
        print(f"❌ Error posting to endpoint: {e}")
        exit(1)
    
    print("\n" + "="*70)
    print("📝 SUMMARY:")
    print("="*70)
    print(f"  Topic: {topic}")
    print(f"  Title: {title}")
    print(f"  Status: Posted successfully")
    print("="*70)


if __name__ == "__main__":
    run()