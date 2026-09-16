---
title: "Troubleshoot a Question Test Case Failure"
title_slug: "troubleshoot-a-question-test-case-failure"
source_url: "https://support.hackerrank.com/articles/5960524158-troubleshoot-a-question-test-case-failure"
article_slug: "5960524158-troubleshoot-a-question-test-case-failure"
last_updated_exact: "July 16, 2026, 11:00 AM"
last_updated_relative: "Last updated 2 months ago"
breadcrumbs:
  - "Library"
  - "Questions"
---

# Troubleshoot a Question Test Case Failure

_Last updated: July 16, 2026, 11:00 AM (Last updated 2 months ago)_

If a question does not evaluate as expected, inspect its test cases, constraints, expected outputs, and checker configuration before changing the candidate-facing problem statement.

# Prerequisites

- Permission to edit questions in **HackerRank for Work**.
- The affected coding question.
- A reproducible failing input or candidate submission.

# Review test cases

To investigate a test case failure:

1. Log in to your **HackerRank for Work** account using your credentials.
2. Open **Library** and locate the affected question.
3. Open the question's test case or evaluation configuration.
4. Identify the input that produces the unexpected result.
5. Compare the expected output with the intended problem behavior.
6. Review constraints and edge cases that may affect evaluation.
7. Check the question's custom checker or evaluation configuration when applicable.
8. Update the test case or expected behavior and save the question.
9. Run the question with representative inputs before returning it to active assessment use.

**Note:** Do not fix a test case solely to make one candidate submission pass. Confirm the intended problem behavior first and test multiple edge cases after the change.

For custom evaluation, see [📄 Custom Checker](/articles/6287413950).
