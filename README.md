# Blog Agent - AI-Powered Blog Writer

An automated blog writing tool powered by Google Gemini AI that generates SEO-optimized blog posts and can publish them to Medium and Dev.to.

## Features

- 🤖 AI-powered blog generation using Google Gemini 2.5 Flash
- 📝 SEO-optimized content with proper markdown formatting
- 🚀 Auto-publish to Medium and Dev.to
- 💾 Automatic saving to local files
- 📊 Word count and character statistics

## Prerequisites

- Python 3.8+
- Google Gemini API Key ([Get one here](https://aistudio.google.com/app/apikey))
- Optional: Medium API Key ([Get from settings](https://medium.com/me/settings/security))
- Optional: Dev.to API Key ([Get from extensions](https://dev.to/settings/extensions))

## Installation

1. Clone the repository:
```powershell
git clone https://github.com/22ECr058/Blogagent.git
cd Blogagent
```

2. Create a virtual environment:
```powershell
python -m venv gemini-env
.\gemini-env\Scripts\Activate.ps1
```

3. Install dependencies:
```powershell
pip install langchain-google-genai langchain-core requests
```

## Configuration

Set your API keys as environment variables:

### Windows PowerShell:
```powershell
# Required: Google Gemini API Key
$env:GOOGLE_API_KEY = "your_gemini_api_key_here"

# Optional: Publishing platform API keys
$env:MEDIUM_API_KEY = "your_medium_api_key"
$env:DEVTO_API_KEY = "your_devto_api_key"
```

### For Permanent Setup:
Add to your PowerShell profile or create a `.env` file (not tracked by git):
```powershell
# To add permanently to your profile:
notepad $PROFILE
# Then add the $env:GOOGLE_API_KEY line to the file
```

## Usage

Run the blog agent:
```powershell
python blogagent.py
```

Follow the prompts:
1. Enter your blog topic
2. Wait for generation (30-60 seconds)
3. Choose whether to publish automatically or manually

Generated blogs are saved in the `blogs/` directory.

## Project Structure

```
Blogagent/
├── blogagent.py          # Main application
├── chatbot.py           # (Other scripts)
├── blogs/               # Generated blog posts
├── gemini-env/          # Virtual environment (not in git)
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## Security Notes

- **Never commit API keys to git**
- API keys are loaded from environment variables only
- The `.gitignore` file excludes `.env` files automatically
- Keep your API keys secure and rotate them regularly

## Publishing

### Manual Publishing:
1. Copy the generated markdown file
2. Paste to:
   - [Medium](https://medium.com/new-story)
   - [Dev.to](https://dev.to/new)
   - [Hashnode](https://hashnode.com/create)

### Auto Publishing:
Set the `MEDIUM_API_KEY` or `DEVTO_API_KEY` environment variables and choose "y" when prompted.

## Troubleshooting

**Error: "GOOGLE_API_KEY environment variable not set!"**
- Make sure you've set the environment variable in your current PowerShell session
- Run: `$env:GOOGLE_API_KEY = "your_key_here"`

**Import errors:**
- Activate your virtual environment: `.\gemini-env\Scripts\Activate.ps1`
- Reinstall dependencies: `pip install -r requirements.txt`

## License

MIT License - Feel free to use and modify!

## Contributing

Pull requests are welcome! For major changes, please open an issue first.
