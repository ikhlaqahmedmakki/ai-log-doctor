# Cron Job Setup Guide

This guide explains how to schedule the AI Log Doctor to run automatically every hour on a Linux server.

## Crontab Expression

To run `scripts/run_doctor.sh` every hour and log all output and errors to `reports/cron.log`, add the following line to your crontab:

```cron
0 * * * * cd /path/to/ai-log-doctor && /bin/bash scripts/run_doctor.sh /path/to/your/application.log >> reports/cron.log 2>&1
```

> **Note:** Replace `/path/to/ai-log-doctor` with the absolute path to your project directory, and `/path/to/your/application.log` with the path to the log file you wish to monitor.

---

## Instructions for Installation

1. Open your terminal on the Linux server.
2. Open the crontab editor for the current user by running:
   ```bash
   crontab -e
   ```
3. Scroll to the bottom of the file and paste the crontab line shown above (making sure to update the absolute paths to match your server environment).
4. Save and close the editor (if using `nano`, press `Ctrl+O`, `Enter`, then `Ctrl+X`; if using `vim`, press `Esc`, type `:wq`, and press `Enter`).
5. Verify that the cron job was successfully installed by listing active cron jobs:
   ```bash
   crontab -l
   ```
