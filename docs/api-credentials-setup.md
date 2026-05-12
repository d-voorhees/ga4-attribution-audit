# API Credentials Setup

This guide covers configuring live data pulls for the GA4 Attribution Audit Toolkit.

## GA4 Data API (Service Account)

1. Create a Google Cloud project or use an existing one.
2. Enable the **Google Analytics Data API**.
3. Create a service account and download the JSON key file.
4. In GA4 Admin, add the service account email as a Viewer on the property.
5. Set environment variables:

```bash
export GA4_PROPERTY_ID=123456789
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

Copy `.env.example` to `.env` and fill in your values for persistent local use.

## Google Ads API (Optional)

Live Google Ads pulls require a developer token and OAuth credentials.

1. Apply for a Google Ads API developer token.
2. Create OAuth 2.0 credentials in Google Cloud Console.
3. Generate a refresh token using the Google Ads OAuth flow.
4. Set environment variables:

```bash
export GOOGLE_ADS_DEVELOPER_TOKEN=your_token
export GOOGLE_ADS_CLIENT_ID=your_client_id
export GOOGLE_ADS_CLIENT_SECRET=your_client_secret
export GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
export GOOGLE_ADS_CUSTOMER_ID=123-456-7890
export GOOGLE_ADS_LOGIN_CUSTOMER_ID=123-456-7890  # if using MCC
```

In `config.yaml`, set `sources.google_ads.mode` to `api` and provide `customer_id`.

## CallRail

CallRail does not expose a public API in this toolkit. Export calls from CallRail as CSV and point `sources.callrail.path` to the file.

Standard export columns used: Start Time, Duration, Caller Number, Tracking Phone Number, Landing Page URL, gclid, utm_source, utm_medium, utm_campaign.

## Security Notes

- Never commit `.env`, service account JSON, or real client CSV exports.
- The `.gitignore` excludes `*_real.csv` patterns and credential files.
- Use read-only service account permissions where possible.
