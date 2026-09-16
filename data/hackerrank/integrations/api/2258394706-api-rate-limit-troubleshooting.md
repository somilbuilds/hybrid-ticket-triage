---
title: "API Rate Limit Troubleshooting"
title_slug: "api-rate-limit-troubleshooting"
source_url: "https://support.hackerrank.com/articles/2258394706-api-rate-limit-troubleshooting"
article_slug: "2258394706-api-rate-limit-troubleshooting"
last_updated_exact: "August 17, 2026, 1:30 PM"
last_updated_relative: "Last updated 1 month ago"
breadcrumbs:
  - "Integrations"
  - "API"
---

# API Rate Limit Troubleshooting

_Last updated: August 17, 2026, 1:30 PM (Last updated 1 month ago)_

API requests can be rejected when an integration sends requests faster than the configured service limits. Review the response and adjust request frequency before retrying.

# Prerequisites

- Access to the application making API requests to **HackerRank for Work**.
- The API response or error message.
- Permission to modify the calling integration.

# Handle rate-limit responses

To troubleshoot API rate limits:

1. Log in to your **HackerRank for Work** account using your credentials when you need to review API configuration.
2. Identify the API request that returned the rate-limit response.
3. Record the request time, endpoint, response status, and any retry information.
4. Review whether the integration sends repeated requests for the same resource.
5. Add retry handling with an appropriate delay when supported by your integration design.
6. Reduce unnecessary polling and batch requests where the API supports batching.
7. Monitor subsequent requests to confirm that the error rate decreases.
8. If the issue persists, collect request examples and timestamps for investigation.

**Note:** Repeating a failed request immediately can increase the number of rejected requests. Use controlled retries rather than an aggressive retry loop.

For authentication failures, see [📄 Webhook API Token Expired](/articles/3957261840).
