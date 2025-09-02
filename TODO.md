## 🔮 Next Steps / Roadmap

* [x] Finish readme
* [x] Add necessary project files
* [x] Push to github
* [x] See what's best to get transcripts (3P web/API, or scrapping)
* [x] docs: Update Readme to switch to simpler local python setup
* [x] build: Switch to simpler local python setup
* [x] feat: Give a video URL and print the summary to stdout
* [x] config: add limits on the openai api usage
* [x] feat: Give a channel id and use the channel's RSS feed URL to print the summary of the latest video to stdout (see https://webapps.stackexchange.com/questions/111680/how-to-find-channel-rss-feed-on-youtube for how to get the RSS feed url, https://www.youtube.com/feeds/videos.xml?channel_id=UCoVoOvIX90IMEZCbBf_ycEA)
* [x] feat: change output to markdown, display the title, the date and video url before the video summary
* [ ] test: Add tests for faster feedback loop, as a way to drive the AI
    * [*] test: Add an e2e test using approvals
    * [ ] test: Fake the summarizer to make it deterministic
    * [ ] test: setup TCR and experiment using the incremental re-test from pypy
    * [ ] test: fake youtube-transcript-api
    * [ ] test: fake rss download
* [ ] test: AI experiment to turn tests into Gherkin
* [ ] test: test for edge and corner cases
* [ ] feat: Given a channel id, save the summary to an md file in a folder named after the channel id
* [ ] feat: Given a channel id, use the output folder to know what is the next video to deal with, and summarize, output and update CSV
* [ ] feat: Same as above, but now use a given number of videos, not just the single next
* [ ] feat: When 3 or more summaries to share, create a summary of summaries
* [ ] feat: Share the summaries as an email
