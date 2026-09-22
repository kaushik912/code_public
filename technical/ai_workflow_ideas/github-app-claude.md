/install-github-app
Sample: spring-learning/.github/workflows

Adds 2 workflows:
- claude.yml - PR Assistant, responds to @claude mentions in issues/PRs
- claude-code-review.yml - auto code review on PR open/update

Setup: run /install-github-app in target repo, auth via GitHub app install, picks up ANTHROPIC_API_KEY or Claude Code OAuth from repo secrets.