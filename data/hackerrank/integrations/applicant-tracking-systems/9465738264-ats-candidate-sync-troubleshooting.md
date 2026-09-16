---
title: "Troubleshoot ATS Candidate Sync"
title_slug: "troubleshoot-ats-candidate-sync"
source_url: "https://support.hackerrank.com/articles/9465738264-troubleshoot-ats-candidate-sync"
article_slug: "9465738264-troubleshoot-ats-candidate-sync"
last_updated_exact: "September 5, 2026, 11:40 AM"
last_updated_relative: "Last updated 2 weeks ago"
breadcrumbs:
  - "Integrations"
  - "Applicant Tracking Systems"
---

# Troubleshoot ATS Candidate Sync

_Last updated: September 5, 2026, 11:40 AM (Last updated 2 weeks ago)_

If candidate information is not appearing correctly between your applicant tracking system and HackerRank for Work, check the integration connection, candidate identifiers, and synchronization status.

# Prerequisites

- Administrator access to the ATS integration in **HackerRank for Work**.
- Access to the corresponding ATS.
- A candidate record that demonstrates the sync issue.

# Check synchronization

To troubleshoot a candidate sync:

1. Log in to your **HackerRank for Work** account using your credentials.
2. Open **Integrations** and select the connected applicant tracking system.
3. Confirm that the integration is enabled and authenticated.
4. Search for the affected candidate and compare the candidate's email and identifying fields in both systems.
5. Review the integration activity or synchronization status for recent errors.
6. Confirm that the candidate is in a stage supported by the integration workflow.
7. Correct the source candidate record or integration configuration as needed.
8. Retry synchronization and verify that the updated candidate data appears in **HackerRank for Work**.

**Note:** Avoid creating a second candidate record while troubleshooting. Duplicate records can make it harder to determine which ATS record is being synchronized.

For stage-specific issues, see [📄 ATS Stage Missing HackerRank Option](/articles/4168372950).
