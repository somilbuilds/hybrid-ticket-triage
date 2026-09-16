---
title: "User Locked Out"
title_slug: "user-locked-out"
source_url: "https://support.hackerrank.com/articles/8624159375-user-locked-out"
article_slug: "8624159375-user-locked-out"
last_updated_exact: "August 27, 2026, 3:40 PM"
last_updated_relative: "Last updated 21 days ago"
breadcrumbs:
  - "Settings"
  - "User Management"
---

# User Locked Out

_Last updated: August 27, 2026, 3:40 PM (Last updated 21 days ago)_

This article explains how to troubleshoot a user who cannot access HackerRank for Work. Check the user's account status, organization membership, and authentication method before changing permissions.

# Prerequisites

- You must have administrator access to the organization.
- Confirm the user's work email address.
- Determine whether the organization uses password authentication or single sign-on.

# Restoring access

To troubleshoot a locked-out user:

1. Log in to your **HackerRank for Work** account using your credentials.
2. Navigate to **Settings** and select **Users**.
3. Search for the affected user by name or email address.
4. Open the user's profile and review the account status.
5. If the user is disabled, select **Enable User** when available.
6. Verify that the user is still a member of the correct organization or team.
7. If password authentication is enabled, ask the user to use **Forgot Password** from the sign-in page if they cannot remember their password.
8. If your organization uses SSO, verify that the user's account is active in the identity provider.
9. Ask the user to sign in again with the email address associated with the HackerRank for Work account.

**Note:** Password resets do not resolve authentication issues controlled by an organization's identity provider. For SSO users, the identity provider must allow access to HackerRank for Work.

If the user can sign in but cannot access a particular feature, review their assigned role and permissions. See [📄 Managing Users and Roles](/articles/3617952048).
