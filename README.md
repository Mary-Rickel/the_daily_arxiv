[![Need help debugging this repo? Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/Mary-Rickel/the_daily_arxiv)
# The Daily arXiv

The Daily ArXiv grabs the 10 (default) latest and relevant papers from arXiv's public API (default category is astro-ph.GA). The code runs automatically once a day (and optionally twice a day with no repeats). Papers are ranked by interest with 1 being highest interest and 3 being lowest. The Daily ArXiv notifies via macOS notification banners and by opening a google chrome page linking to the paper.

All repeats are skipped (tracked in `seen_papers.json`)

## Dependencies

**Required:**
- macOS
- Python 3 (standard libraries only)
- Google Chrome

**Optional but highly recommended** (I can't promise the code won't bark at you without it):
- Homebrew
- `terminal-notifier` (if you don't have this, run `brew install terminal-notifier`)

## Getting started

**1. (If downloading not cloning) Put the folder somewhere permanent**

```bash
mv ~/Downloads/the_daily_arxiv ~/the_daily_arxiv
cd ~/the_daily_arxiv
```

**2. Set notifications to Alerts (Optional but helpful)**
To have the banners stay on screen until dismissed:

Got to System Settings → Notifications → Terminal → **Alerts**

**3. Run the installer**

```bash
chmod +x install.sh
./install.sh
```
After running the installer, you will be prompted with several options. Just follow along and answer the prompts as they come up. An option for a test run is included.

## Editing your keywords

To edit your key words to fit your preference, either open the config.json file directly and edit or run the following command:

```bash
python3 ~/the_daily_arxiv/the_daily_arxiv.py --settings
```

Opens `config.json` in TextEdit. Use double quotes ONLY. Single quotes will break the file and the code will not work.

## Ranking
The Daily ArXiv Ranks queried papers by how many of your keywords appear in the title and abstract (called hits) :
   - **Rank 1** — 5 or more keyword hits (high interest)
   - **Rank 2** — 2–4 keyword hits (moderate interest)
   - **Rank 3** — 1 keyword hit (low interest)

## Commands

**Manual runs:**
- `python3 the_daily_arxiv.py --am` — run the AM fetch now
- `python3 the_daily_arxiv.py --pm` — run the PM fetch now

**Configuration:**
- `python3 the_daily_arxiv.py --settings` — open keyword/config editor
- `python3 the_daily_arxiv.py --check` — check setup and print current config
- `python3 the_daily_arxiv.py --clear-seen` — reset seen-papers log (re-notifies everything)

**Installation:**
- `bash install.sh` — install or reinstall the scheduled tasks
- `bash uninstall.sh` — remove the LaunchAgent scheduled tasks


## Config reference (`config.json`)

| Key | Default | Description |
|---|---|---|
| `category` | [`astro-ph.IM`, `astro-ph.EP`] | arXiv category (or optionally categories) to fetch |
| `keywords` | — | Terms searched in title + abstract |
| `max_papers` | `80` | How many papers to fetch from arXiv |
| `max_notifications` | `10` | Max banners per run |
| `delay_between` | `6` | Seconds between each notification |
| `only_matched` | `true` | Only notify on keyword matches |
| `seen_expiry_days` | `7` | Days before a paper can be re-shown |

## Troubleshooting

**No notifications appearing**
- Check System Settings → Notifications → Terminal → set to Alerts
- Run `python3 the_daily_arxiv.py --check` to verify setup
- Check `daily_arxiv.log` for errors

**"Google Chrome" not found error**
- Make sure Chrome is installed in `/Applications/Google Chrome.app`
- If you use a different browser, edit the `open -a "Google Chrome"` lines in the script

**Seeing fewer than 10 papers**
- Your keywords may not match enough papers. To fix this, try adding more by opening config.json or `--settings`
- Or run `--clear-seen` if the seen log is filtering too aggressively

**Previous/different versions of an installation are running simultaneously**

When you run `launchctl list | grep arxiv` you should only see `- 0 com.thedailyarxiv.pm` and `- 0 com.thedailyarxiv.am`. If 
see more than this, as an example `-2 com.thedailyarxiv.am`, you will have to unload previous versions otherwise you will run into a query limit error "HTTP ERROR 429: Too Many Requests".

To unload, you will have to do run the following commands (in this order):
- `launchctl unload ~/Library/LaunchAgents/NAME_OF_EXTRA_RUN`, where you would replace NAME_OF_EXTRA_RUN with whatever the name is. 
- `rm ~/Library/LaunchAgents/NAME_OF_EXTRA_RUN.plist`


## Acknowledgements

Developed with assistance from [Claude](https://claude.ai) (Anthropic).
