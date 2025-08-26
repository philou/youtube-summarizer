
# YouTube Channel Summarizer (Python, Local, CSV)

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

youtube-summarizer/
├── .env.example           # Example environment variables (API keys, etc.)
├── .gitignore             # Python, env, and local ignores
├── LICENSE                # MIT License
├── README.md              # Project documentation
├── main.py                # Main script entry point
├── requirements.txt       # Python dependencies
├── videos.csv             # Output CSV file (URL, title, summary, ...)
└── utils.py               # Helper functions (fetching, summarizing, etc.)
```

## 🚀 Local Usage

### Prerequisites
- Python 3.9 or newer
- Install dependencies:

  ```bash
  pip install -r requirements.txt
  ```

### Setup & Usage

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/your-repo.git
   cd your-repo
   ```

2. **Configure environment variables:**

   Copy `.env.example` to `.env` and fill in any required API keys or settings.

3. **Run the script:**

   ```bash
   python main.py
   ```

4. **(Optional) Schedule with cron:**

   You can schedule the script to run weekly using cron or your OS scheduler.

## Design Choice: Simplicity & Portability

* No cloud dependencies: everything runs locally.
* Uses a simple CSV file as the database.
* Easy to run manually or schedule.
* Python ecosystem allows easy transcript fetching and future extensibility.

## 📧 Notifications

Whenever the script runs, if new videos are found:
  * They are added to the CSV file
  * An email digest is sent, using Python's `smtplib` and `email` modules.

