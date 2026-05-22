# The Daily arXiv

The Daily ArXiv grabs the 10 (default) latest and relevant papers to you from arXiv's public API (default category is astro-ph.GA). The code runs automatically once a day (and optionally twice a day with no repeats). Papers are ranked by interest with 1 being highest interest and 3 being lowest. The Daily ArXiv notifies via macOS notification banners and by opening a google chrome page linking to the paper.

All repeats are skipped (tracked in `seen_papers.json`)


## Ranking
The Daily ArXiv Ranks queried papers by how many of your keywords appear in the title and abstract (called hits) :
   - **Rank 1** — 5 or more keyword hits (high interest)
   - **Rank 2** — 2–4 keyword hits (moderate interest)
   - **Rank 3** — 1 keyword hit (low interest)

## Dependencies

**Required:**
- macOS
- Python 3 (standard libraries only — no pip installs needed)
- Google Chrome

**Optional but highly recommended** (I can't promise the code won't bark at you without it):
- Homebrew
- `terminal-notifier` — `brew install terminal-notifier`

## Getting started

**1. Put the folder somewhere permanent**

Don't run it from Downloads, move it somewhere else:

```bash
mv ~/Downloads/the_daily_arxiv ~/the_daily_arxiv
cd ~/the_daily_arxiv
```

**2. Set notifications to Alerts (Optional but helpful)**
To have the banners stay on screen until dismissed:

Got to System Settings → Notifications → Terminal → **Alerts**

**3. Run the installer**

```bash
bash install.sh
```
After running the installer, you will be prompted with several options. Just follow along and answer the prompts as they come up. An option for a test run is included.

## Editing your keywords

To edit your key words to fit your preference, either open the config.json file directly and edit or run the following command:

```bash
python3 ~/the_daily_arxiv/the_daily_arxiv.py --settings
```

Opens `config.json` in TextEdit. Use double quotes ONLY. Single quotes will break the file and the code will not work.

## All commands

 `python3 the_daily_arxiv.py --am` Runs the AM fetch manually 
 `python3 the_daily_arxiv.py --pm` Runs the PM fetch manually 
 `python3 the_daily_arxiv.py --settings` Opens editor to set keywords and config 
 `python3 the_daily_arxiv.py --check` Checks setup and prints config
 `python3 the_daily_arxiv.py --clear-seen` Reset seen-papers log (re-notifies everything)
 `bash install.sh` Install or reinstall the schedule
 `bash uninstall.sh` Remove the LaunchAgent scheduled tasks


## Config reference (`config.json`)

arXiv category to fetch : `category` `astro-ph.GA`  
Terms searched in title + abstract : `keywords` 
How many papers to fetch from arXiv: `max_papers`  `80` 
Max banners per run: `max_notifications` `10` 
Seconds between each notification: `delay_between` `6` 
Only notify on keyword matches: `only_matched` `true` 
How many days before a paper can be re-shown: `seen_expiry_days`  `7`

## Troubleshooting

**No notifications appearing**
- Check System Settings → Notifications → Terminal → set to Alerts
- Run `python3 the_daily_arxiv.py --check` to verify setup
- Check `daily_arxiv.log` for errors

**"Google Chrome" not found error**
- Make sure Chrome is installed in `/Applications/Google Chrome.app`
- If you use a different browser, edit the `open -a "Google Chrome"` lines in the script

**Seeing fewer than 10 papers**
- Your keywords may not match enough papers — broaden them in `--settings`
- Or run `--clear-seen` if the seen log is filtering too aggressively

## Acknowledgements

Developed with assistance from [Claude](https://claude.ai) (Anthropic).
