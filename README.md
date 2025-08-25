# YouTube Channel Summarizer to Google Sheets

This project automates the process of collecting and summarizing YouTube videos from a channel’s RSS feed. It saves results into a Google Sheet and notifies via email when new videos are available.

## ✨ Features

* Fetch videos from a YouTube channel’s **RSS feed**
* Download transcripts for each new video (via transcript APIs or scraping fallback)
* Summarize each video transcript using an LLM
* Save results (URL, title, summary) into a Google Sheet
* Send an email digest of new videos:

  * If fewer than 3 videos → list them with summaries
  * If 3+ videos → also send a **“summary of summaries”**

## 🛠 Tech Stack & Tools

* **Google Apps Script**: main runtime (easy Google Sheets integration + email sending)
* **clasp**: local development tool for Apps Script.

  * Allows you to write, version, and debug your Apps Script locally.
  * Sync code between GitHub and Google Apps Script.
* **Google Sheets**: used as the project’s lightweight database.
* **External transcript fetching**: (still has to be decided)

  * Option A: Use YouTube APIs / existing transcript services with APIs.
  * Option B: Scrape transcripts from YouTube if APIs not available.

## 📂 Project Structure

```
youtube-summarizer/
├── .env.example           # Example environment variables
├── .gitignore             # Node, clasp, and local ignores
├── .nvmrc                 # Node version for nvm
├── LICENSE                # MIT License
├── README.md              # Project documentation
├── clasp.json             # clasp config for Apps Script
├── jest.config.js         # Jest test config
├── package.json           # npm dependencies and scripts
├── package-lock.json      # npm lockfile
├── src/                   # Source code
│   ├── index.js           # Main entry point
│   └── sheets.js          # Google Sheets abstraction layer
└── coverage/              # Jest test coverage output (gitignored)
```

## 🚀 Local Development

To make development easier, we use **npm** for dependency management, **jest** for testing, and **clasp** for syncing code with Google Apps Script.

### Prerequisites
- Node.js (>= 22)
- npm (ships with Node.js)
- A Google account with access to Google Apps Script
- `clasp` installed globally

```bash
npm install -g @google/clasp
```

### Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/your-repo.git
   cd your-repo
   ```

2. **Install dependencies:**

   ```bash
   npm install
   ```

   This will install Jest and any other project dependencies.

3. **Login to Google with clasp:**

   ```bash
   clasp login
   ```

4. **Create or link to your Apps Script project:**

   * To create a new project:

     ```bash
     clasp create --type sheets --title "YouTube Summarizer"
     ```
   * Or to link to an existing project:

     ```bash
     clasp clone <script-id>
     ```

5. **Push code to Apps Script:**

   ```bash
   clasp push
   ```

6. **Pull code changes from Apps Script:**

   ```bash
   clasp pull
   ```

### Running Locally

Since Apps Script APIs are not available locally, we use an abstraction layer to mock interactions (e.g., spreadsheets).
You can run local tests with:

```bash
npm test
```

### Workflow

* Write and test your logic locally with Jest.
* Use mocks for spreadsheet or Gmail functions in local tests.
* Push working code to Apps Script with `clasp push`.
* Debug directly in Apps Script if needed.

## Design Choice: Local Abstraction Layer

Instead of coding only inside Apps Script, we’ll create a **Google Sheets abstraction** (`sheets.js`).

* When running locally: it can mock the sheet with a CSV file.
* When deployed: it will connect to the real Google Sheet via Apps Script API.

👉 This allows **faster iteration and testing locally** while still being easy to deploy.

## 📧 Notifications

* The script checks RSS feed regularly (e.g. via time-based trigger).
* If new videos are found:

  * They are added to the Google Sheet.
  * An email digest is sent automatically.

