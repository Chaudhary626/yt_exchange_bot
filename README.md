# YouTube Engagement Exchange Bot

A Telegram bot to exchange YouTube engagement in an anti-fraud, task-based, proof-verified way.

## Features

- Submit your YouTube video for promotion (max 5 at a time)
- Help others by watching, liking, commenting, subscribing
- Proof-upload and owner-verified system
- Fair exchange: you must help others before your video is shown
- Anti-fraud, timeout, and reporting system
- All actions via inline buttons and Telegram commands

## Commands

- `/start` - Welcome message & instructions
- `/submit` - Submit a new YouTube video
- `/videos` - List & remove your videos
- `/match` - Get a task to help others
- `/proof` - Upload your proof of helping
- `/verify` - Approve/reject proofs for your videos
- `/report` - Report invalid proof or cheaters

## Project Structure

```
yt_exchange_bot/
│
├── bot.py
├── config.py
├── database.py
│
├── handlers/
│   ├── start_handler.py
│   ├── submit_handler.py
│   ├── match_handler.py
│   ├── proof_handler.py
│   ├── verify_handler.py
│   ├── video_handler.py
│   └── report_handler.py
│
├── requirements.txt
└── README.md
```

## Database

Uses `sqlite3` with tables: users, videos, reports

## Deployment

### Local (Termux)

1. Install Python 3 and pip
2. `pip install -r requirements.txt`
3. Set your `BOT_TOKEN` in `config.py` or as an environment variable
4. `python bot.py`

### Hosting (Render/Replit)

- Set environment variables: `BOT_TOKEN`, `ADMIN_IDS` (comma separated)
- The bot is designed for always-on hosting.

## Notes

- All core exchanges are locked by proof/verification.
- 15-minute timeouts and anti-fraud are enforced.
- If your proof is not verified within 15 minutes, you can proceed to the next task.
- Admins get notified for every report.

---