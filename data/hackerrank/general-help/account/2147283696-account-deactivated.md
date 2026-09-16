---
title: "Account Deactivated or Suspended"
title_slug: "account-deactivated-or-suspended"
source_url: "https://support.hackerrank.com/articles/2147283696-account-deactivated-or-suspended"
article_slug: "2147283696-account-deactivated-or-suspended"
last_updated_exact: "August 8, 2026, 9:25 AM"
last_updated_relative: "Last updated 1 month ago"
breadcrumbs:
  - "General Help"
  - "Account"
---

# Account Deactivated or Suspended

_Last updated: August 8, 2026, 9:25 AM (Last updated 1 month ago)_

If a user cannot sign in because their HackerRank for Work account is inactive, an administrator should verify the account status and the organization's identity-management configuration.

# Prerequisites

- Organization administrator or user-management access.
- The affected user's email address.
- Access to the organization's identity provider when SSO or SCIM is enabled.

# Check account status

To investigate an inactive account:

1. Log in to your **HackerRank for Work** account using your credentials.
2. Open **Settings** and select **User Management**.
3. Search for the affected user by email address.
4. Review whether the account is active, inactive, suspended, or otherwise restricted.
5. If the account was manually deactivated, restore access when appropriate for your organization's policy.
6. If SCIM is enabled, check whether the identity provider has deprovisioned or disabled the user.
7. Confirm the user's assigned role and authentication method.
8. Ask the user to sign in again after the account status has been corrected.

**Note:** If SCIM controls the user's lifecycle, changing the account manually may be temporary because the next provisioning update can apply the identity provider's state again.

For SSO and provisioning configuration, see [📄 SSO and SCIM Provisioning](/articles/9476839274).
