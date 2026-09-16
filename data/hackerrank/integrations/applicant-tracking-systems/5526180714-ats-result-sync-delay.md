---
title: "ATS Result Sync Is Delayed"
title_slug: "ats-result-sync-is-delayed"
source_url: "https://support.hackerrank.com/articles/5526180714-ats-result-sync-is-delayed"
article_slug: "5526180714-ats-result-sync-is-delayed"
last_updated_exact: "July 20, 2026, 3:05 PM"
last_updated_relative: "Last updated 1 month ago"
breadcrumbs:
  - "Integrations"
  - "Applicant Tracking Systems"
---

# ATS Result Sync Is Delayed

_Last updated: July 20, 2026, 3:05 PM (Last updated 1 month ago)_

If a completed HackerRank for Work assessment result has not appeared in the ATS, verify the candidate mapping, integration status, and recent synchronization activity.

# Prerequisites

- Access to the connected ATS integration.
- Permission to view candidate results.
- The candidate's record in both systems.

# Troubleshoot result synchronization

To investigate a delayed result:

1. Log in to your **HackerRank for Work** account using your credentials.
2. Open the relevant test and locate the candidate's completed attempt.
3. Confirm that the result is finalized and contains the expected score.
4. Open **Integrations** and review the connected ATS status.
5. Compare the candidate email and identifiers in both systems.
6. Review recent integration activity for a failed or pending result event.
7. Retry the synchronization when the integration supports a manual retry.
8. Confirm that the result appears in the expected ATS candidate record.

**Note:** A finalized result in HackerRank for Work does not necessarily mean the ATS has already processed the corresponding integration event. Check the event status before sending another result manually.

For broader ATS troubleshooting, see [📄 Troubleshoot ATS Candidate Sync](/articles/9465738264).
