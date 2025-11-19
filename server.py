"""
Simple Flask server to receive blog posts
"""
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from datetime import datetime
import json
import os
import httpx
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Store blogs in memory (you can save to file/database later)
blogs = []

# Load API key from environment
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# HTML template to display blogs
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Blog Generator</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .generate-section {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        .input-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #333;
        }
        input[type="text"] {
            width: 100%;
            padding: 12px;
            font-size: 16px;
            border: 2px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        button {
            background: #3498db;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            cursor: pointer;
            width: 100%;
        }
        button:hover {
            background: #2980b9;
        }
        button:disabled {
            background: #95a5a6;
            cursor: not-allowed;
        }
        .status {
            margin-top: 15px;
            padding: 15px;
            border-radius: 4px;
            display: none;
        }
        .status.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .status.loading {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        .blog-container {
            display: grid;
            gap: 20px;
        }
        .blog-post {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .blog-title {
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .blog-meta {
            color: #7f8c8d;
            font-size: 0.9em;
            margin-bottom: 15px;
        }
        .blog-content {
            line-height: 1.6;
            color: #34495e;
        }
        .topic-badge {
            display: inline-block;
            background: #3498db;
            color: white;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 0.85em;
            margin-bottom: 10px;
        }
        .no-blogs {
            text-align: center;
            color: #7f8c8d;
            padding: 40px;
        }
    </style>
</head>
<body>
    <h1>📝 AI Blog Generator</h1>
    
    <div class="generate-section">
        <h2>Generate New Blog</h2>
        <div class="input-group">
            <label for="topic">Enter Blog Topic:</label>
            <input type="text" id="topic" placeholder="e.g., What is AI?, Benefits of Python, etc." />
        </div>
        <button onclick="generateBlog()">🚀 Generate Blog</button>
        <div id="status" class="status"></div>
    </div>
    
    <h2>Generated Blogs</h2>
    <div class="blog-container">
        {% if blogs %}
            {% for blog in blogs %}
            <div class="blog-post">
                <span class="topic-badge">{{ blog.topic }}</span>
                <h2 class="blog-title">{{ blog.title }}</h2>
                <div class="blog-meta">
                    Posted: {{ blog.timestamp }}
                </div>
                <div class="blog-content">
                    {{ blog.content[:500] }}...
                    <br><br>
                    <a href="/blog/{{ loop.index0 }}">Read full post</a>
                </div>
            </div>
            {% endfor %}
        {% else %}
            <div class="no-blogs">
                <h3>No blog posts yet</h3>
                <p>Enter a topic above and click "Generate Blog" to create your first post!</p>
            </div>
        {% endif %}
    </div>
    
    <script>
        function generateBlog() {
            const topic = document.getElementById('topic').value.trim();
            const status = document.getElementById('status');
            const button = document.querySelector('button');
            
            if (!topic) {
                status.className = 'status error';
                status.style.display = 'block';
                status.textContent = '❌ Please enter a topic';
                return;
            }
            
            status.className = 'status loading';
            status.style.display = 'block';
            status.textContent = '⏳ Generating blog... This may take 30-60 seconds...';
            button.disabled = true;
            
            fetch('/generate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({topic: topic})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    status.className = 'status success';
                    status.textContent = '✅ Blog generated successfully!';
                    setTimeout(() => location.reload(), 1500);
                } else {
                    status.className = 'status error';
                    status.textContent = '❌ Error: ' + data.error;
                    button.disabled = false;
                }
            })
            .catch(error => {
                status.className = 'status error';
                status.textContent = '❌ Error: ' + error.message;
                button.disabled = false;
            });
        }
        
        document.getElementById('topic').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') generateBlog();
        });
    </script>
</body>
</html>
"""

BLOG_DETAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ blog.title }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .blog-post {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
        }
        .blog-meta {
            color: #7f8c8d;
            margin-bottom: 20px;
        }
        .blog-content {
            line-height: 1.8;
            color: #34495e;
        }
        .back-link {
            display: inline-block;
            margin-bottom: 20px;
            color: #3498db;
            text-decoration: none;
        }
        .back-link:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <a href="/" class="back-link">← Back to all posts</a>
    <div class="blog-post">
        <h1>{{ blog.title }}</h1>
        <div class="blog-meta">
            Topic: {{ blog.topic }} | Posted: {{ blog.timestamp }}
        </div>
        <div class="blog-content">
            {{ blog.content | safe }}
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    """Display all blog posts"""
    return render_template_string(HTML_TEMPLATE, blogs=blogs)

@app.route('/blog/<int:blog_id>')
def blog_detail(blog_id):
    """Display single blog post"""
    if blog_id < len(blogs):
        return render_template_string(BLOG_DETAIL_TEMPLATE, blog=blogs[blog_id])
    return "Blog not found", 404

@app.route('/generate', methods=['POST'])
def generate_blog():
    """Generate blog using AI"""
    try:
        data = request.get_json()
        topic = data.get('topic', '').strip()
        
        if not topic:
            return jsonify({'success': False, 'error': 'Topic is required'}), 400
        
        if not GOOGLE_API_KEY:
            return jsonify({
                'success': False,
                'error': 'GOOGLE_API_KEY environment variable not set. Set it with: $env:GOOGLE_API_KEY="your_key"'
            }), 500
        
        # Initialize Gemini with timeout settings
        # Create HTTP client with custom timeout (60 seconds)
        http_client = httpx.Client(
            timeout=httpx.Timeout(60.0, connect=10.0),
            limits=httpx.Limits(max_connections=5, max_keepalive_connections=2)
        )
        
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=GOOGLE_API_KEY,
            temperature=0.7,
            max_tokens=8192,
            timeout=60,
            max_retries=2
        )
        
        # Create prompt
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
        
        # Generate blog
        chain = prompt | llm | StrOutputParser()
        content = chain.invoke({"topic": topic})
        
        # Extract title
        title = "Untitled Blog Post"
        for line in content.strip().split('\n'):
            if line.startswith('# '):
                title = line[2:].strip()
                break
        
        # Save blog
        blog_post = {
            'title': title,
            'content': content,
            'topic': topic,
            'timestamp': datetime.now().isoformat()
        }
        
        blogs.append(blog_post)
        
        # Save to file
        with open('blogs_data.json', 'w', encoding='utf-8') as f:
            json.dump(blogs, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ New blog generated: {title}")
        
        return jsonify({
            'success': True,
            'message': 'Blog generated successfully',
            'blog_id': len(blogs) - 1
        }), 201
        
    except httpx.TimeoutException:
        error_msg = 'Request timed out. Google API may be experiencing issues. Please try again in a few minutes.'
        print(f"❌ Timeout Error: {error_msg}")
        return jsonify({'success': False, 'error': error_msg}), 504
    except httpx.ConnectError as e:
        error_msg = f'Cannot connect to Google API. Check your internet connection.'
        print(f"❌ Connection Error: {e}")
        return jsonify({'success': False, 'error': error_msg}), 503
    except Exception as e:
        error_msg = str(e)
        if 'timeout' in error_msg.lower():
            error_msg = 'Request timed out after 60 seconds. Try again or check your API quota.'
        elif '503' in error_msg or 'connect' in error_msg.lower():
            error_msg = 'Google API is temporarily unavailable. Please try again in a few minutes.'
        elif '429' in error_msg:
            error_msg = 'API quota exceeded. Wait for quota reset or use a different API key.'
        print(f"❌ Error: {e}")
        return jsonify({'success': False, 'error': error_msg}), 500

@app.route('/blogs', methods=['POST'])
def create_blog():
    """Receive blog post from the blog agent"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'title' not in data or 'content' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: title and content'
            }), 400
        
        # Add blog to list
        blog_post = {
            'title': data.get('title'),
            'content': data.get('content'),
            'topic': data.get('topic', 'General'),
            'timestamp': data.get('timestamp', datetime.now().isoformat())
        }
        
        blogs.append(blog_post)
        
        # Save to file (optional)
        with open('blogs_data.json', 'w', encoding='utf-8') as f:
            json.dump(blogs, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ New blog received: {blog_post['title']}")
        print(f"   Total blogs: {len(blogs)}")
        
        return jsonify({
            'success': True,
            'message': 'Blog post created successfully',
            'blog_id': len(blogs) - 1,
            'total_blogs': len(blogs)
        }), 201
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/blogs', methods=['GET'])
def get_blogs():
    """Get all blogs as JSON"""
    return jsonify({
        'success': True,
        'total': len(blogs),
        'blogs': blogs
    })

if __name__ == '__main__':
    # Load existing blogs if file exists
    if os.path.exists('blogs_data.json'):
        try:
            with open('blogs_data.json', 'r', encoding='utf-8') as f:
                blogs = json.load(f)
            print(f"📚 Loaded {len(blogs)} existing blog(s)")
        except:
            pass
    
    print("\n" + "="*60)
    print("🚀 Blog Server Starting...")
    print("="*60)
    print("📝 View blogs at: http://127.0.0.1:5500")
    print("📮 POST endpoint: http://127.0.0.1:5500/blogs")
    print("📊 API endpoint: http://127.0.0.1:5500/api/blogs")
    print("="*60 + "\n")
    
    app.run(host='127.0.0.1', port=5500, debug=True)
