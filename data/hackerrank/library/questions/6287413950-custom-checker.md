---
title: "Custom Checker"
title_slug: "custom-checker"
source_url: "https://support.hackerrank.com/articles/6287413950-custom-checker"
article_slug: "6287413950-custom-checker"
last_updated_exact: "September 5, 2026, 12:15 PM"
last_updated_relative: "Last updated 12 days ago"
breadcrumbs:
  - "Library"
  - "Questions"
---

# Custom Checker

_Last updated: September 5, 2026, 12:15 PM (Last updated 12 days ago)_

A custom checker lets a coding question use evaluation logic beyond a direct comparison between the candidate output and a fixed expected output. Configure and validate the checker carefully before adding the question to an assessment.

# Prerequisites

- You must have permission to edit the coding question.
- Confirm that the question requires custom evaluation behavior.
- Prepare and test the checker logic with representative outputs.

# Configuring a custom checker

To configure a custom checker:

1. Log in to your **HackerRank for Work** account using your credentials.
2. Navigate to **Library** and open the relevant coding question.
3. Select **Edit** and open the question's evaluation settings.
4. Select the available **Custom Checker** option.
5. Enter or upload the checker configuration supported for the question.
6. Review the checker inputs and expected evaluation behavior.
7. Save the question.
8. Run the question with valid, invalid, and boundary-case submissions.
9. Confirm that the checker accepts correct solutions and rejects incorrect solutions.
10. Publish the question after validation is complete.

**Note:** A checker should validate the required output behavior without relying on candidate-specific assumptions. Test cases that pass a flawed checker can produce incorrect candidate scores.

If the checker does not behave as expected, review the checker input and output format and test it independently with representative cases. See [📄 Hidden Test Cases](/articles/5176382940).
