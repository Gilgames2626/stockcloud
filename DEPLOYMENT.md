# AlphaHunter V1.5.2 Final - Cloud deployment

## 1. Upload to GitHub

Create or use a repository and upload the **contents** of this folder to the repository root. `app.py` must be visible in the root.

Do not upload:
- `.env`
- `.streamlit/secrets.toml`
- `data/cache.db`

## 2. Deploy on Streamlit Community Cloud

1. Sign in at `https://share.streamlit.io` with GitHub.
2. Select **Create app**.
3. Select the repository and branch.
4. Main file path: `app.py`.
5. Open **Advanced settings**.
6. Python version: `3.12`.
7. Paste the following into **Secrets** with real values:

```toml
GEMINI_API_KEY = "your-real-key"
GEMINI_MODEL = "gemini-3.5-flash-lite"
SEC_USER_AGENT = "AlphaHunter Your Name your.email@example.com"
```

8. Click **Deploy**.

## 3. Restrict access

In app settings, open **Sharing** and choose **Only specific people can view this app**. Invite only the email addresses that should have access.

## 4. Important cloud-cache limitation

The current SQLite cache is suitable for local use and for temporary acceleration in one cloud instance. Streamlit Community Cloud does not guarantee persistent local storage. A reboot or redeploy may remove `data/cache.db`, after which the app will rebuild its cache and may make new Gemini calls.

This does not affect the analysis logic, but it can affect speed and API usage after a reboot. A future production deployment should move the persistent cache to an external database such as PostgreSQL or Supabase.
