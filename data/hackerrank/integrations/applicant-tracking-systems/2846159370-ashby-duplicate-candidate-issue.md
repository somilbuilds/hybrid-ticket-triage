---
title: "Ashby Duplicate Candidate Issue"
title_slug: "ashby-duplicate-candidate-issue"
source_url: "https://support.hackerrank.com/articles/2846159370-ashby-duplicate-candidate-issue"
article_slug: "2846159370-ashby-duplicate-candidate-issue"
last_updated_exact: "September 3, 2026, 1:35 PM"
last_updated_relative: "Last updated 14 days ago"
breadcrumbs:
  - "Integrations"
  - "Applicant Tracking Systems"
  - "Ashby"
---

# Ashby Duplicate Candidate Issue

_Last updated: September 3, 2026, 1:35 PM (Last updated 14 days ago)_

This article explains how to troubleshoot duplicate candidate records created when Ashby synchronizes with HackerRank for Work. Verify candidate identifiers and integration mappings before removing or modifying records.

# Prerequisites

- The Ashby integration must be enabled.
- You must have administrator access to the integration.
- Confirm the affected candidate records in both systems.

# Troubleshooting duplicate candidates

To troubleshoot duplicate candidate records:

1. Log in to your **HackerRank for Work** account using your credentials.
2. Navigate to **Settings** and select **Integrations**.
3. Open the **Ashby** integration and verify that the connection is active.
4. Compare the candidate's email address and other available identifiers in Ashby and HackerRank for Work.
5. Check whether the candidate is associated with more than one job or application in Ashby.
6. Review recent synchronization activity for duplicate or failed records.
7. Verify that the integration has the required permissions to read candidate and application data.
8. Correct duplicate candidate information in the source system when appropriate.
9. Run or wait for the next synchronization and verify the candidate mapping.

**Note:** A candidate can appear more than once when separate application records or mismatched identifiers are treated as different candidates. Avoid deleting records until the source application and existing assessment history have been reviewed.

If duplicates continue to appear, record the candidate identifiers and synchronization timestamps before contacting support. See [📄 Troubleshoot ATS Candidate Sync](/articles/6175283049).
