---
title: "Greenhouse Sync Failed"
title_slug: "greenhouse-sync-failed"
source_url: "https://support.hackerrank.com/articles/7519348264-greenhouse-sync-failed"
article_slug: "7519348264-greenhouse-sync-failed"
last_updated_exact: "September 2, 2026, 4:20 PM"
last_updated_relative: "Last updated 15 days ago"
breadcrumbs:
  - "Integrations"
  - "Applicant Tracking Systems"
  - "Greenhouse"
---

# Greenhouse Sync Failed

_Last updated: September 2, 2026, 4:20 PM (Last updated 15 days ago)_

This article explains how to troubleshoot synchronization failures between Greenhouse and HackerRank for Work. Common causes include expired authorization, missing permissions, and inactive job configurations.

# Prerequisites

- The Greenhouse integration must be configured for your HackerRank for Work account.
- You must have administrator permissions.
- Confirm that the affected job or candidate exists in Greenhouse.

# Troubleshooting the Greenhouse integration

To troubleshoot a failed sync:

1. Log in to your **HackerRank for Work** account using your credentials.
2. Navigate to **Settings** and select **Integrations**.
3. Open **Greenhouse** and review the integration status.
4. Verify that the connection is authorized and has not expired.
5. Confirm that the Greenhouse user or API credentials have the required permissions.
6. Verify that the affected job is active in Greenhouse.
7. Review the synchronization history and note any displayed error message.
8. If authorization is invalid, select **Reconnect** or the available authorization option.
9. Retry the synchronization and verify that the affected record is updated.

**Note:** Changes to permissions in Greenhouse can cause an existing integration connection to fail. Reauthorizing the integration does not automatically correct job-level configuration or missing permissions.

If the sync continues to fail, record the exact error message, affected job, and candidate before contacting support. See [📄 Configure Greenhouse Integration](/articles/4926718305).
