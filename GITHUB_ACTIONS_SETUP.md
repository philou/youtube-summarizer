# GitHub Actions Deployment Setup

## Overview
This setup uses GitHub Actions as a serverless cron service with git as persistent storage. Each YouTube channel gets its own branch for automated daily processing.

## 🔧 Setup Instructions

### 1. Configure Repository Secrets
Go to your repository Settings → Secrets and variables → Actions, and add these secrets:

- **`OPENAI_API_KEY`**: Your OpenAI API key for transcript summarization
- **`GMAIL_USERNAME`**: Your Gmail address (e.g., `your-email@gmail.com`)  
- **`GMAIL_PASSWORD`**: Your Gmail app password (not your regular password)
- **`RECIPIENT_EMAIL`**: Email address to receive summary notifications

### 2. Set Up Gmail App Password
1. Enable 2-factor authentication on your Google account
2. Go to Google Account Settings → Security → App passwords
3. Generate a new app password for "Mail"
4. Use this app password as `GMAIL_PASSWORD` secret

### 3. Create Channel Branches

For each YouTube channel you want to monitor, create a dedicated branch:

```bash
# Example: Monitor channel UCoVoOvIX90IMEZCbBf_ycEA  
git checkout -b channel-UCoVoOvIX90IMEZCbBf_ycEA
git push -u origin channel-UCoVoOvIX90IMEZCbBf_ycEA

# Example: Monitor another channel
git checkout -b channel-UCxyz123
git push -u origin channel-UCxyz123

# Return to main branch
git checkout main
```

**Branch naming convention:** `channel-{YOUTUBE_CHANNEL_ID}`

### 4. How to Find YouTube Channel IDs

1. **Method 1**: Go to the channel page and check the URL:
   - `https://www.youtube.com/@channelname` → View page source → search for `"channelId"`
   
2. **Method 2**: Use online tools like [Keyword Recon](https://keywordrecon.com/articles/how-to-view-youtube-channel-id/)

### 5. Quick Setup Script (Optional)

If you have multiple channels, you can create them all at once:

```bash
# Create multiple channel branches
CHANNELS=("UCoVoOvIX90IMEZCbBf_ycEA" "UCxyz123" "UCabc456")

for channel in "${CHANNELS[@]}"; do
    echo "Creating branch for channel: $channel"
    git checkout -b "channel-$channel"
    git push -u origin "channel-$channel"
done

# Return to main
git checkout main
echo "✅ All channel branches created!"
```

## 🚀 How It Works

### Automatic Daily Runs
- **Schedule**: Runs daily at 9 AM UTC on all `channel-*` branches
- **Channel Detection**: Extracts channel ID from branch name automatically
- **Processing**: Downloads new video transcripts, generates summaries, commits files
- **Notifications**: Sends HTML email with summaries

### Manual Triggering
You can manually trigger workflows:
1. Go to **Actions** tab in GitHub
2. Select **"YouTube Summarizer"** workflow
3. Click **"Run workflow"**
4. Choose the channel branch and optionally set max summaries

### Branch Safety
- ✅ Only runs on branches starting with `channel-`
- ✅ Main branch is protected from automatic runs
- ✅ Workflow files remain in main branch for easy maintenance
- ✅ No infinite loops - only triggers on schedule/manual, not on commits

## 📁 File Organization

After running, your repository will look like:
```
repository/
├── .github/workflows/youtube-summarizer.yml  # Workflow definition
├── youtube_summarizer.py                     # Main application
├── requirements.txt                          # Dependencies
└── UCoVoOvIX90IMEZCbBf_ycEA/                # Channel folder (auto-created)
    ├── video1.md                             # Individual summaries
    ├── video2.md
    └── video3.md
```

## 📊 Monitoring

### Check Run Status
- **Actions Tab**: View all workflow runs and their status
- **Email Notifications**: Configure GitHub to email you on workflow failures
- **Commit History**: Each run creates commits with new summary files

### Logs and Debugging
- Click on any workflow run in the Actions tab to see detailed logs
- Summary report shows channel processed and file count
- Git operations are logged for troubleshooting

## ⚙️ Configuration Options

### Customize Schedule
Edit `.github/workflows/youtube-summarizer.yml`:
```yaml
schedule:
  - cron: '0 18 * * *'  # Run at 6 PM UTC instead
```

### Change Summary Limits
Default is 5 summaries per run. Modify in workflow or use manual trigger with custom value.

### Add More Channels
Simply create more `channel-*` branches - each will run independently.

## 🔒 Security Features

- ✅ **Secrets Management**: API keys stored securely in GitHub secrets
- ✅ **Isolated Branches**: Each channel runs independently
- ✅ **Read-only Main**: Main branch never executes automated workflows
- ✅ **Git Authentication**: Uses GitHub's built-in token for commits

## 🚨 Troubleshooting

### Common Issues

**Workflow not running:**
- Check branch name starts with `channel-`
- Verify secrets are configured correctly
- Ensure branch is pushed to GitHub

**Git commit failures:**
- Check if channel folder is in `.gitignore`
- Verify GitHub token has write permissions
- Look for file permission issues in logs

**Email not sending:**
- Verify Gmail app password (not regular password)
- Check 2-factor authentication is enabled
- Confirm GMAIL_USERNAME format is correct

### Getting Help
- Check the Actions tab for detailed error logs
- Review commit history for successful runs
- Test locally first with `--git-commits-off` flag

## 🎯 Next Steps

1. **Set up your first channel branch**
2. **Configure all required secrets**
3. **Test with manual workflow trigger**
4. **Monitor first scheduled run**
5. **Add more channels as needed**

This setup provides a robust, serverless solution for automated YouTube channel monitoring with zero ongoing maintenance!