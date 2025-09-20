
# YouTube Channel Summarizer

This project automates the process of collecting and summarizing YouTube videos from a channel's RSS feed. It downloads video transcripts, summarizes them using AI, saves the results as markdown files, and sends email notifications with the summaries.

## ✨ Features

* **Fetch videos** from a YouTube channel's RSS feed
* **Download transcripts** for each new video using the [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)
* **AI-powered summaries** using OpenAI's GPT models
* **Save results** as markdown files in channel-specific folders
* **Email notifications** with HTML-formatted summaries
* **Git integration** for automatic commits and version history
* **GitHub Actions deployment** for automated daily runs
* **Multi-channel support** via branch-based deployment strategy

## 🛠 Tech Stack & Tools

* **Python 3.9+**
* **youtube-transcript-api**: fetch YouTube video transcripts
* **OpenAI API**: for intelligent transcript summarization
* **yagmail**: simplified Gmail integration for email notifications
* **GitPython**: for automatic git commits and version control
* **Markdown**: for HTML email formatting
* **GitHub Actions**: for automated scheduling and deploymentummarizer (Python, Local, CSV)

This project automates the process of collecting and summarizing YouTube videos from a channel’s RSS feed. It downloads video transcripts using Python, summarizes them, and saves the results into a local CSV file. You can run the script manually or schedule it (e.g. with cron).

## ✨ Features

* Fetch videos from a YouTube channel’s **RSS feed**
* Download transcripts for each new video using the [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)
* Summarize each video transcript using an LLM (e.g. OpenAI API, optional)
* Save results (URL, title, summary) into a local CSV file
* Send an email digest of new videos

## 🛠 Tech Stack & Tools

* **Python 3.9+**
* **youtube-transcript-api**: fetch YouTube video transcripts
* **csv**: built-in Python module for CSV file handling
* **openai**: for transcript summarization
* **smtplib/email**: for sending email digests

## 📁 Project Structure

```
youtube-summarizer/
├── .env.example              # Example environment variables (API keys, etc.)
├── .gitignore               # Python, env, and channel folder ignores
├── LICENSE                  # MIT License
├── README.md               # Project documentation
├── DECISION_LOG.md         # Architecture decision records
├── TODO.md                 # Project roadmap and tasks
├── youtube_summarizer.py   # Main application code
├── requirements.txt        # Python dependencies
├── tests/                  # Test suite
│   ├── test_youtube_summarizer.py     # Unit tests
│   └── test_youtube_summarizer_e2e.py # End-to-end tests
└── [CHANNEL_ID]/           # Generated summary folders
    ├── video1.md           # Individual video summaries
    ├── video2.md
    └── ...
```

## 🚀 Usage

### Prerequisites
- Python 3.9 or newer
- OpenAI API key
- Gmail account with app password
- Git repository (for version control)

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/philou/youtube-summarizer.git
   cd youtube-summarizer
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   Copy `.env.example` to `.env` and fill in your credentials:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your actual values:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   GMAIL_USERNAME=your_email@gmail.com
   GMAIL_PASSWORD=your_app_password_here
   ```

### Local Usage

**Basic usage (no git commits):**
```bash
python youtube_summarizer.py UC_CHANNEL_ID user@example.com --git-commits-off
```

**With git commits enabled:**
```bash
python youtube_summarizer.py UC_CHANNEL_ID user@example.com --git-commits-on
```

**Limit number of videos processed:**
```bash
python youtube_summarizer.py UC_CHANNEL_ID user@example.com --git-commits-on 5
```

### GitHub Actions Deployment

For automated daily runs, see the [GitHub Actions setup guide](GITHUB_ACTIONS_SETUP.md).

## 📧 Email Features

The tool automatically sends HTML-formatted email summaries containing:
- **Individual video summaries** with titles, content, and metadata
- **Meta-summary** when processing multiple videos (AI-generated overview)
- **Smart subject lines** (video title for single videos, count for multiple)
- **Rich formatting** with proper HTML conversion from markdown

## 🧪 Testing

The project includes comprehensive test coverage:

**Run unit tests:**
```bash
python -m unittest tests/test_youtube_summarizer.py -v
```

**Run end-to-end tests (requires real API keys):**
```bash
python -m unittest tests/test_youtube_summarizer_e2e.py -v
```

**Skip slow tests:**
```bash
# If using pytest (optional)
pytest -m "not slow"
```

## 🏗️ Architecture

### Design Principles
- **Testable**: Comprehensive test suite with fakes and mocks
- **Modular**: Clean separation between transcription, summarization, email, and git operations
- **Configurable**: Environment-based configuration for different deployment scenarios
- **Version controlled**: All summaries are tracked in git with full history

### Key Components
- **YoutubeSummarizer**: Main orchestrator class
- **Summarizer**: OpenAI integration for AI-powered summaries
- **YoutubeTranscription**: Transcript fetching from YouTube
- **GitRepository**: Version control integration
- **Email Service**: HTML email notifications via Gmail

## � Deployment Options

### Option 1: Local Cron (Traditional)
Schedule the script to run locally using cron or task scheduler.

### Option 2: GitHub Actions (Recommended)
- **Zero server maintenance**: GitHub handles infrastructure
- **Branch-based channels**: Each YouTube channel gets its own branch
- **Automatic scheduling**: Daily runs via GitHub's cron
- **Built-in persistence**: Git serves as the database
- **Cost effective**: Works on GitHub's free tier

## Design Choice: Git as Database

- **No external database**: Everything stored in git repository
- **Full history**: Every summary is versioned and auditable  
- **Distributed**: Easy to backup, clone, and share
- **Simple deployment**: No database setup or maintenance required

