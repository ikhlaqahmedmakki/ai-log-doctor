# 🩺 AI Log Doctor

An automated, LLM-powered log monitoring and diagnostic agent designed for DevOps and Cloud Engineers. **AI Log Doctor** automatically collects error logs from your applications, filters and snapshots failures, uses OpenAI GPT models to diagnose root causes and suggest remediations, persists findings in an SQLite database with deduplication, and sends instant high-priority alerts directly to Discord.

---

## 🏗️ Architecture Diagram

```text
  [ Application / Server Logs ]
                │
                ▼
      ( scripts/collect_logs.sh )
                │
                ▼
       [ reports/latest_snapshot.txt ]
                │
                ▼
      ( Python Core Agent: src/doctor.py )
                │
          ┌─────┴─────┐
          │           │
          ▼           ▼
   [ SQLite DB ]  [ OpenAI LLM API ]
   (doctor.db)    (gpt-4o-mini)
          │           │
          └─────┬─────┘
                │
          (Deduplicated?)
          ├── Yes ──► [ Ignore / Log Duplicate ]
          └── No  ──► [ Save & Evaluate Severity ]
                      ├── Low / Medium ──► [ Print Diagnosis ]
                      └── High / Critical ──► [ Discord Webhook Alert 🚨 ]
```

---

## 🛠️ Tech Stack

- **Language:** Python 3.10+
- **Shell Automation:** Bash (`set -euo pipefail`)
- **Database:** SQLite3 (Lightweight, zero-config persistent storage)
- **AI / LLM:** OpenAI API (`gpt-4o-mini` with JSON response mode)
- **Notifications:** Discord Webhooks (HTTP POST via `requests`)
- **Scheduling:** Linux `cron`

---

## ⚙️ Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# OpenAI API configuration
LLM_API_KEY=your_openai_api_key_here
API_BASE_URL=https://api.openai.com/v1

# Optional: Discord Webhook URL for High/Critical alerts
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook_id/your_webhook_token
```

---

## 🚀 Installation & Local Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/ai-log-doctor.git
cd ai-log-doctor
```

### 2. Set Up Virtual Environment & Dependencies
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Configure Environment
Copy or create your `.env` file in the project root and populate your `LLM_API_KEY` and optional `DISCORD_WEBHOOK_URL`.

### 4. Run Manually
You can run the full pipeline using the wrapper script:
```bash
bash scripts/run_doctor.sh /path/to/your/application.log
```

---

## ⏰ Automated Production Monitoring (Cron)

To run the AI Log Doctor automatically every hour on a Linux server:

1. Open your crontab:
   ```bash
   crontab -e
   ```
2. Add the following cron job (update absolute paths to match your environment):
   ```cron
   0 * * * * cd /path/to/ai-log-doctor && /bin/bash scripts/run_doctor.sh /path/to/your/application.log >> reports/cron.log 2>&1
   ```

For detailed scheduling instructions, see [cron_setup.md](./cron_setup.md).
