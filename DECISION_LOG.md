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
