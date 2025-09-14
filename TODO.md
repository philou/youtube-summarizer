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
* [*] test: Add tests for faster feedback loop, as a way to drive the AI
    * [*] test: Add an e2e test using approvals
    * [*] test: Fake the summarizer to make it deterministic
    * [*] test: fake youtube-transcript-api
    * [*] test: fake rss download
        * Up to now, I'm really disappointed by how the AI is helping me...
    * [*] test: capture the results without going through patching stdout
    * [*] refactor: pass the channel id as arg to run instead of using argv
* [*] feat: Given a channel id, save the summary to an md file in a folder named after the channel id
* [*] feat: Given a channel id, use the output folder to know what are the missing videos to deal with
* [*] feat: Same as above, but now use a given number of videos, not just the single next
    - [x] did too much in 1 batch -> revert and cherry pick
    - [x] add the feature
    - [x] change the main to accept an argument
    - [x] rename main to youtube_summarizer
* [x] refactor: introduct feed builder in tests
* [*] feat: Share the summaries as an email
* [ ] refactor: extract methods in the main function
* [ ] feat: When 3 or more summaries to share, create a summary of summaries
* [ ] feat: generate email subject from content
* [ ] test: test for edge and corner cases

## Parking
* [ ] feat: convert the markdown to html for the email
* [ ] refactor: make methods private
* [ ] refactor: migrate to pytest to have real "slowTest" tags and allow to run e2e test without commenting the skip annotation
* [ ] test: setup TCR for fast flow, and try to help AI with this
* [ ] refactor: clean up the abstraction level in main
* [ ] test: migrate to pytest and replace @unitest.skip with @pytest.mark.slow
