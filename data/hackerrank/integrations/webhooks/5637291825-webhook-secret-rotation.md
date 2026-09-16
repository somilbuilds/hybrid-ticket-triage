---
title: "Rotate a Webhook Secret"
title_slug: "rotate-a-webhook-secret"
source_url: "https://support.hackerrank.com/articles/5637291825-rotate-a-webhook-secret"
article_slug: "5637291825-rotate-a-webhook-secret"
last_updated_exact: "July 19, 2026, 10:35 AM"
last_updated_relative: "Last updated 2 months ago"
breadcrumbs:
  - "Integrations"
  - "Webhooks"
---

# Rotate a Webhook Secret

_Last updated: July 19, 2026, 10:35 AM (Last updated 2 months ago)_

Rotate a webhook secret when credentials may have been exposed or your organization's security policy requires periodic credential changes. Coordinate the change with the receiving application.

# Prerequisites

- Administrator access to the webhook configuration.
- Access to the receiving application.
- A maintenance window if the receiving application cannot accept overlapping credentials.

# Rotate the secret

To rotate a webhook secret:

1. Log in to your **HackerRank for Work** account using your credentials.
2. Open **Settings** and locate the relevant **Webhook** configuration.
3. Review the current webhook and identify the receiving endpoint.
4. Generate or reveal the replacement secret using the available security action.
5. Update the receiving application with the new secret.
6. Verify that the receiving application validates requests using the new value.
7. Save the updated webhook configuration when required.
8. Trigger a test event and confirm that the receiving application accepts the request.

**Note:** Rotating a secret can immediately invalidate the previous value. Do not rotate credentials without confirming that the receiving system can be updated at the same time.

For delivery failures, see [📄 Troubleshoot Failed Webhook Deliveries](/articles/9576849375).
