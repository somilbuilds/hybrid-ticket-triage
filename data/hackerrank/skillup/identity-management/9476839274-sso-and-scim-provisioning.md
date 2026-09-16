---
title: "SSO and SCIM Provisioning"
title_slug: "sso-and-scim-provisioning"
source_url: "https://support.hackerrank.com/articles/9476839274-sso-and-scim-provisioning"
article_slug: "9476839274-sso-and-scim-provisioning"
last_updated_exact: "August 25, 2026, 3:45 PM"
last_updated_relative: "Last updated 3 weeks ago"
breadcrumbs:
  - "SkillUp"
  - "Identity Management"
---

# SSO and SCIM Provisioning

_Last updated: August 25, 2026, 3:45 PM (Last updated 3 weeks ago)_

Single sign-on (SSO) controls how users authenticate, while SCIM provisioning can automate user creation, updates, and deprovisioning. Configure both services with matching identity-provider attributes and access rules.

# Prerequisites

- Organization administrator access to **HackerRank for Work**.
- Administrator access to your identity provider.
- Required SSO metadata and SCIM configuration values.

# Configure SSO and SCIM

To configure identity management:

1. Log in to your **HackerRank for Work** account using your credentials.
2. Open **Settings** and locate the organization's **SSO** or authentication settings.
3. Enter or upload the identity provider information required for SSO.
4. Save the SSO configuration and test sign-in with an authorized account.
5. Open the **SCIM** provisioning settings.
6. Generate or copy the provisioning credentials and endpoint information required by your identity provider.
7. Configure user and group provisioning in the identity provider.
8. Map required attributes such as email and name.
9. Test provisioning with a controlled user before enabling broader synchronization.

**Note:** SCIM deprovisioning can remove or disable user access when a user is removed from the identity provider. Confirm group assignments and attribute mappings before enabling automatic provisioning for the organization.

For role-related access issues, see [📄 Role Permission Missing](/articles/9625483170).
