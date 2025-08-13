# Celery Worker Restart Instructions

## Overview

This guide provides step-by-step instructions to restart the Celery worker with the updated configuration that disables email notifications to resolve network connectivity errors.

## Current Configuration Status

✅ **Email notifications have been disabled** in `src/backend/.env`:

```
ENABLE_EMAIL_NOTIFICATIONS=False
```

## Restart Process

### Step 1: Stop the Current Celery Worker

The Celery worker is currently running in Terminal 13. To stop it:

1. **Switch to Terminal 13** (or the terminal running the Celery worker)
2. **Press `Ctrl+C`** to gracefully stop the worker
3. **Wait for the shutdown message** confirming the worker has stopped

### Step 2: Restart the Celery Worker

After stopping the worker, restart it with the updated configuration:

```bash
cd src/backend && celery -A app.worker.celery_app worker --loglevel=info
```

**Alternative method** (if you're already in the project root):

```bash
celery -A src.backend.app.worker.celery_app worker --loglevel=info --workdir=src/backend
```

### Step 3: Verify the Configuration is Loaded

After restarting, look for these log messages to confirm email notifications are disabled:

```
[INFO] Email notifications are disabled
[WARNING] Email service not configured or disabled. Would have sent email to [email] with subject: [subject]
```

## Expected Behavior After Restart

### ✅ What Should Work:

- Contract analysis tasks should complete successfully
- No more "[Errno 8] nodename nor servname provided, or not known" errors
- Email notification attempts will be logged but not executed
- All other functionality remains intact

### 🔍 What to Monitor:

- Check that contract analysis completes without network errors
- Verify that email-related log messages show "disabled" status
- Ensure task processing continues normally

## Troubleshooting

### If the Worker Fails to Start:

1. **Check Redis connection**: Ensure Redis is running on localhost:6379
2. **Verify Python environment**: Ensure all dependencies are installed
3. **Check working directory**: Make sure you're in the correct directory

### If Network Errors Persist:

1. **Verify .env file**: Confirm `ENABLE_EMAIL_NOTIFICATIONS=False` is set
2. **Check configuration loading**: Look for the "Email notifications are disabled" log message
3. **Clear any cached settings**: Restart the FastAPI backend server as well

## Additional Commands

### To check Celery worker status:

```bash
cd src/backend && celery -A app.worker.celery_app inspect active
```

### To purge all pending tasks (if needed):

```bash
cd src/backend && celery -A app.worker.celery_app purge
```

### To restart all services (comprehensive restart):

1. Stop Celery worker (Ctrl+C in Terminal 13)
2. Stop FastAPI backend (Ctrl+C in Terminal 11)
3. Restart FastAPI: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
4. Restart Celery: `celery -A app.worker.celery_app worker --loglevel=info`

## Configuration Details

The email notification system is controlled by:

- **Environment variable**: `ENABLE_EMAIL_NOTIFICATIONS=False` in `.env`
- **Settings class**: `src/backend/app/core/config.py` line 18
- **Email service**: `src/backend/app/services/email_service.py` checks this setting

When disabled, the `EmailService.is_configured()` method returns `False`, preventing any SMTP connection attempts and eliminating the DNS resolution errors.
