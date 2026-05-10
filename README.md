# Bloomberg Technology Automation

Automated system to fetch, analyze, and report on Bloomberg Technology daily shows using Google Gemini AI.

## Features

- **Automated Video Fetching**: Automatically discovers the latest Bloomberg Technology videos from YouTube
- **Transcript Extraction**: Downloads video transcripts/captions
- **AI-Powered Analysis**: Uses Google Gemini to generate:
  - Daily summaries of key tech news
  - Trading insights for tech stocks
  - Key takeaways for investors
  - Weekly highlights for review
- **Markdown Reports**: Generates daily reports and maintains a master weekly review document
- **Smart Tracking**: Prevents duplicate processing of videos
- **Scheduled Execution**: Run automatically via cron or Task Scheduler

## Project Structure

```
bloomberg-tech-tracker/
├── scripts/
│   ├── main.py                    # Main orchestration script
│   ├── youtube_fetcher.py         # YouTube video & transcript fetcher
│   ├── gemini_analyzer.py         # Gemini AI analyzer
│   ├── markdown_generator.py      # Report generator
│   └── setup_scheduler.py         # Scheduler setup utility
├── reports/
│   ├── daily/                     # Daily markdown reports
│   └── weekly_review_master.md    # Master weekly review doc
├── config/
│   ├── config.json               # Configuration file
│   └── processed_videos.json     # Tracks processed videos
├── logs/
│   └── automation.log            # Execution logs
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Prerequisites

- Python 3.8 or higher
- Google Gemini API key
- Internet connection

## Installation

### 1. Clone or Download

If you haven't already, navigate to the project directory:

```bash
cd bloomberg-tech-tracker
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Get Google Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

### 5. Configure

**A. Copy the config template:**

```bash
cp config/config.json.example config/config.json
```

**B. Set your API key via `.env` (recommended):**

```bash
cp .env.example .env
# Edit .env and replace the placeholder with your real key:
# GEMINI_API_KEY=your_actual_key_here
```

`.env` is git-ignored and will never be committed. The key is loaded automatically at runtime.

You can also customize `config/config.json` to adjust:
- Analysis prompts
- Output file paths
- Scheduling time
- Logging settings

## Usage

### Manual Execution

Run the automation manually:

```bash
cd scripts
python main.py
```

### Test Components

Test individual components without processing videos:

```bash
python main.py --test
```

### Set Up Automated Scheduling

Run the scheduler setup script:

```bash
python setup_scheduler.py
```

The script will guide you through setting up:
- **Linux/Mac**: Cron job or systemd timer
- **Windows**: Task Scheduler

Default schedule: Daily at 9:00 AM (customizable)

### Manual Scheduling Setup

#### Linux/Mac - Cron

```bash
# Edit crontab
crontab -e

# Add this line (adjust paths and time as needed):
0 9 * * * cd /path/to/bloomberg-tech-tracker && /path/to/venv/bin/python scripts/main.py >> logs/cron.log 2>&1
```

#### Windows - Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set to run daily at 9:00 AM
4. Program: `C:\path\to\venv\Scripts\python.exe`
5. Arguments: `C:\path\to\bloomberg-tech-tracker\scripts\main.py`
6. Start in: `C:\path\to\bloomberg-tech-tracker`

## Output

### Daily Reports

Generated in `reports/daily/` with filename format: `YYYY-MM-DD_bloomberg_tech.md`

Each report contains:
- Video metadata (title, URL, date, duration)
- Daily summary of tech news
- Trading insights for tech stocks
- Key takeaways
- Weekly highlights

### Master Weekly Review Document

Located at `reports/weekly_review_master.md`

Contains accumulated highlights and important points for weekly review of tech news and trading opportunities.

## Configuration

Key configuration options in `config/config.json`:

### API Keys

Set your Gemini API key in `.env` (preferred):

```
GEMINI_API_KEY=your_key_here
```

Or fall back to `config/config.json`:

```json
"api_keys": {
  "gemini_api_key": "your_key_here"
}
```

### YouTube Settings
```json
"youtube": {
  "channel_id": "UCrM7B7SL_g1edFOnmj-SDKg",
  "video_duration_min": 30
}
```

### Gemini Settings
```json
"gemini": {
  "model": "gemini-pro",
  "temperature": 0.7,
  "analysis_prompts": { ... }
}
```

### Automation Settings
```json
"automation": {
  "check_time": "09:00",
  "timezone": "America/New_York",
  "retry_attempts": 3
}
```

## Troubleshooting

### No videos found

- **Cause**: All recent videos already processed
- **Solution**: Check `config/processed_videos.json` - remove entries if you want to reprocess

### Gemini API errors

- **Cause**: Invalid API key or quota exceeded
- **Solution**:
  - Verify `GEMINI_API_KEY` is set correctly in `.env`
  - Check [Google AI Studio](https://makersuite.google.com/) for quota limits
  - Free tier has rate limits - consider upgrading if needed

### Transcript not available

- **Cause**: Video doesn't have captions/transcript
- **Solution**: System will skip video and try next one automatically

### Import errors

- **Cause**: Missing dependencies
- **Solution**:
  ```bash
  pip install -r requirements.txt
  ```

### Permission denied

- **Cause**: Scripts not executable
- **Solution**:
  ```bash
  chmod +x scripts/*.py
  ```

## Logs

Logs are stored in `logs/automation.log`

To view recent logs:
```bash
tail -f logs/automation.log
```

To view errors only:
```bash
grep ERROR logs/automation.log
```

## Customization

### Modify Analysis Prompts

Edit the `analysis_prompts` section in `config/config.json` to customize what Gemini analyzes:

```json
"analysis_prompts": {
  "daily_summary": "Your custom prompt here...",
  "trading_insights": "Your custom prompt here...",
  ...
}
```

### Change Report Format

Edit `scripts/markdown_generator.py` to customize report layout and formatting.

### Add New Analysis Types

1. Add prompt to `config.json` under `analysis_prompts`
2. Call `gemini_analyzer._generate_analysis()` with new prompt
3. Add to report template in `markdown_generator.py`

## Best Practices

1. **Check logs regularly**: Monitor `logs/automation.log` for issues
2. **Review API usage**: Keep track of Gemini API quota
3. **Backup reports**: Periodically backup `reports/` directory
4. **Update dependencies**: Run `pip install -U -r requirements.txt` monthly
5. **Customize prompts**: Adjust prompts based on your trading focus

## Limitations

- Requires active internet connection
- Bloomberg Technology must publish videos with transcripts
- Gemini API has rate limits (free tier: ~60 requests/min)
- Transcript quality depends on YouTube's auto-captioning or manual transcripts

## Future Enhancements

Potential improvements:
- Support for multiple YouTube channels
- Email/SMS notifications with daily summaries
- Database storage for historical analysis
- Web dashboard for viewing reports
- Sentiment analysis tracking over time
- Integration with trading platforms

## License

This is a personal automation tool. Bloomberg Technology content and trademarks belong to Bloomberg L.P.

## Disclaimer

This tool is for informational and educational purposes only. It does not provide financial advice. Always do your own research before making investment decisions.

## Support

For issues or questions:
1. Check logs in `logs/automation.log`
2. Review this README
3. Test components with `python main.py --test`
4. Verify API keys and configuration

---

**Created**: 2026-01-29
**Version**: 1.0.0
