# Skills.sh
- Use this to install skills **neatly**

# Key links
- https://www.skills.sh/ - leaderboard of all popular skills
- https://www.skills.sh/anthropics

# Installation
- npx skills
- npx skills add https://github.com/anthropics/skills --skill frontend-design

- You can either add at project level or global(user level)
- You could add a skill called `find-skills` at user level that helps in suggesting skills for various tasks.

### How to test
- npx skills list (project specific) 
- npx skills list -g (global)

- When installed, it shows this newly installed skill under `.agents/skills` folder.
- Optional: agent debugging: `github.copilot.chat.agentDebugLog.fileLogging.enabled` in VS code settings. 


# Create own skill
- npx skills init recursive-code-review
- Fill up the relevant sections

# Another way to create complex skill
- npx skills add anthropics/skills@skill-creator
- Then use /skill-creator in prompt. This will help esp in the case of claude.

# update skills
- npx skills update -p(project) or -g(global), or -y (non-interactive update)
- npx skills update skill-creator (for specific skill)

# remove skills
- npx skills remove <skill_name>
- npx skills remove -g
- npx skills remove --agent claude-code cursor <xyz-skill> ( to remove from specific agent)
- To remove all installed skills, you can use
    - npx skills remove --all
- Remove skills from a specific agent using
    - npx skills remove --skill '*' -a github-copilot

# Summary
- Skills.sh help in consistency (file structure, assets, scripts etc). Because LLMs are non-determistic, skills help in adding preferences for certain workflows.
- Also skills CLI is useful to manage skills with different AI assistants.