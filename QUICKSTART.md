# Quick Start Guide

Get Bloomberg Technology automation running in 5 minutes!

## 1. Install Dependencies

```bash
cd bloomberg-tech-tracker
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Get Gemini API Key

1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key

## 3. Configure

```bash
cp .env.example .env
```

Edit `.env` and set your key:

```
GEMINI_API_KEY=PASTE_YOUR_KEY_HERE
```

## 4. Test Run

```bash
cd scripts
python main.py --test
```

If tests pass, run for real:

```bash
python main.py
```

## 5. Set Up Daily Automation

```bash
python setup_scheduler.py
```

Follow the prompts to schedule daily runs.

## What You Get

- **Daily Reports**: `reports/daily/YYYY-MM-DD_bloomberg_tech.md`
- **Weekly Review**: `reports/weekly_review_master.md`
- **Logs**: `logs/automation.log`

## Troubleshooting

**No videos found?**
- Check `config/processed_videos.json` - delete entries to reprocess

**API errors?**
- Verify your Gemini API key
- Check quota at https://makersuite.google.com/

**Import errors?**
- Activate virtual environment: `source venv/bin/activate`
- Reinstall: `pip install -r requirements.txt`

## Next Steps

- Customize analysis prompts in `config/config.json`
- Review logs: `tail -f logs/automation.log`
- Check reports in `reports/` directory

For detailed documentation, see [README.md](README.md)
