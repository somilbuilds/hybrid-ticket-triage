---
title: "SSO Login Fails"
title_slug: "sso-login-fails"
source_url: "https://support.hackerrank.com/articles/3481539260-sso-login-fails"
article_slug: "3481539260-sso-login-fails"
last_updated_exact: "August 3, 2026, 9:45 AM"
last_updated_relative: "Last updated 1 month ago"
breadcrumbs:
  - "Integrations"
  - "SSO"
---

# SSO Login Fails

_Last updated: August 3, 2026, 9:45 AM (Last updated 1 month ago)_

If a user cannot sign in through single sign-on, compare the identity provider configuration with the organization's HackerRank for Work SSO settings and review the exact authentication error.

# Prerequisites

- Administrator access to **HackerRank for Work**.
- Administrator access to the identity provider.
- The affected user's email address and error message.

# Troubleshoot SSO

To troubleshoot an SSO login failure:

1. Log in to your **HackerRank for Work** account using your credentials.
2. Open the organization's **SSO** or authentication settings.
3. Confirm that SSO is enabled and the identity provider configuration is current.
4. Verify the user's email or identifier matches the value expected by the identity provider.
5. Review certificate, metadata, or endpoint configuration when applicable.
6. Check the identity provider's authentication logs for the failed sign-in.
7. Correct the configuration and test with a controlled user.
8. Ask the affected user to sign in again after the configuration is confirmed.

**Note:** Avoid changing multiple SSO settings at once. Isolating the changed value makes it easier to identify the cause of an authentication failure.

For combined identity management, see [📄 SSO and SCIM Provisioning](/articles/9476839274).
