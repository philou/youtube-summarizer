# Decision Log

## 2025-08-26: Use Local Python Script for YouTube Summarizer

**Decision:**
Use a local Python script to fetch YouTube video transcripts, summarize them, and store results in a CSV file.

**Rationale:**
- Simplicity: Easy to run and maintain locally.
- Cost: No need to pay for external APIs or cloud services.
- Capability: Can use the `youtube-transcript-api` Python library, which is not available in Apps Script.

**Alternatives considered:**
- Scraping YouTube or transcript download websites: Too fragile, and not possible in Apps Script.
- Paying for a YouTube transcript online API: Too expensive for this use case.
- Deploying code outside of Apps Script (e.g., cloud functions): Not worth the hassle for a simple workflow.

## 2025-09-19: Deploy through git branches and github actions

## 2025-09-19: Deploy through git branches and github actions

**Decision:**
Deploy the YouTube summarizer using GitHub Actions with channel-specific branches for scheduling and git as persistent storage, with git operations handled in Python code.

**Rationale:**
- **Zero server maintenance**: GitHub handles all infrastructure and scheduling
- **Built-in persistence**: Git repository serves as database for summary files with full history
- **Multi-channel support**: Each YouTube channel gets its own branch (e.g., `channel-UCxxxxx`) 
- **Cost effective**: Works on GitHub free tier with generous action minutes
- **Audit trail**: Every run is logged and traceable through GitHub Actions
- **Scalable**: Easy to add new channels by creating new branches
- **Fully testable**: Git operations in Python code can be unit tested with mocks

**Implementation:**
- Workflow triggers daily via cron schedule on branches matching `channel-*` pattern
- Secrets store API keys (OpenAI, Gmail credentials) securely
- Python code handles git commits using GitPython library after processing summaries
- Smart triggering prevents infinite loops (only runs on schedule, not commits)
- Simplified GitHub Actions workflow - just runs Python script

**Alternatives considered:**
- **Local cron job**: Requires always-on machine, manual setup, no redundancy
- **Cloud functions**: More complex setup, ongoing costs, vendor lock-in
- **Traditional VPS deployment**: Higher maintenance overhead, security concerns
- **Git operations in GitHub Actions YAML**: Harder to test, less control over error handling

**Trade-offs:**
- Slightly more complex Python code with additional GitPython dependency
- Need to handle git authentication and error scenarios in code
- Dependency on GitHub availability for the automation
- Limited to GitHub's action runtime limits (though sufficient for this use case)