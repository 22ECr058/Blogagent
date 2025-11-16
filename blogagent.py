# blogagent.py - Blog Agent with Environment Variables
import os
import requests
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load API keys from environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MEDIUM_API_KEY = os.getenv("MEDIUM_API_KEY", "")
DEVTO_API_KEY = os.getenv("DEVTO_API_KEY", "")

if not GOOGLE_API_KEY:
    print("ERROR: GOOGLE_API_KEY environment variable not set!")
    print("Set it with: $env:GOOGLE_API_KEY='your_api_key_here'")
    exit()

print("Gemini API Key LOADED SUCCESSFULLY!")
print("Blog Agent is READY!\n")

# GEMINI 2.5 FLASH - ONLY WORKING MODEL
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",       # ← CORRECT
    google_api_key=GOOGLE_API_KEY,
    temperature=0.7,
    max_tokens=8192
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

def extract_title(content: str) -> str:
    """Extract title from markdown content"""
    lines = content.strip().split('\n')
    for line in lines:
        if line.startswith('# '):
            return line[2:].strip()
    return "Untitled Blog Post"

def run():
    topic = input("Enter blog topic: ").strip() or "How to Make $10,000/Month with AI in 2025"
    print(f"\n🚀 Generating blog post about: {topic}...")
    print("⏳ This may take 30-60 seconds for a full blog post...\n")
    
    # Generate the blog using the chain
    content = chain.invoke({"topic": topic})
    
    # Extract title from content
    title = extract_title(content)
    
    # Save to file
    os.makedirs("blogs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = "".join(c if c.isalnum() or c in " _-" else "_" for c in topic)
    filename = f"{timestamp}_{safe[:40]}.md"
    file = f"blogs/{filename}"
    
    with open(file, "w", encoding="utf-8") as f:
        f.write(content)
    
    print("="*70)
    print(f"✅ BLOG GENERATED!")
    print("="*70)
    print(f"\n📄 Title: {title}")
    print(f"📁 Saved to: {file}")
    print(f"📊 Length: {len(content)} characters, ~{len(content.split())} words")
    
    # Auto-publish if API keys are configured
    publish_choice = input("\n🚀 Publish now? (y/n, or 'manual' to skip): ").strip().lower()
    
    if publish_choice == 'y':
        print("\n📤 Publishing to platforms...")
        published = []
        
        if MEDIUM_API_KEY:
            if publish_to_medium(title, content):
                published.append("Medium")
        
        if DEVTO_API_KEY:
            if publish_to_devto(title, content):
                published.append("Dev.to")
        
        if not published:
            print("\n⚠️  No publishing platforms configured!")
            print("   Add API keys at the top of blogagent.py to enable auto-publishing.")
    
    print("\n" + "="*70)
    print("📝 NEXT STEPS:")
    print("="*70)
    print("  1. Open the file and review it")
    print("  2. Press Ctrl+Shift+V in VS Code to preview Markdown")
    print("  3. Manual publishing:")
    print(f"     • Medium: Copy/paste to https://medium.com/new-story")
    print(f"     • Dev.to: Copy/paste to https://dev.to/new")
    print(f"     • Hashnode: Copy/paste to https://hashnode.com/create")
    print("  4. Earn $500+ from your content! 💰")
    print("="*70)
    
    print(f"\n📄 Preview (first 600 chars):")
    print("-"*70)
    print(content[:600] + "...")
    print("-"*70)


if __name__ == "__main__":
    run()