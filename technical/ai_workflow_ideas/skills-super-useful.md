/plugin marketplace add anthropics/skills
/plugin, very useful to see what skills are already installed or you can install new skills.

npx skills list -g
npx mcpick list
npx terminal-skills install -h
npx terminal-skills list

## some others noteworthy
superpowers, /brainstorm, /execute-plan

### langchain
npx skills add langchain-ai/langsmith-skills --skill '*' --yes

### project specific ideation using new skills
npx skills add https://github.com/vercel-labs/skills --skill find-skills

## manual search (recommended)
npx skill find 
Then as you type, you'll see the skills matching the keyword.

## caveman (to save tokens)
npx skills add JuliusBrussee/caveman (just for the skills)

- Below if you want plugin ( this is skills + hooks)
claude plugin marketplace add JuliusBrussee/caveman
claude plugin install caveman@caveman

Alternately, claude > /plugins , add a plugin > JuliusBrussee/caveman, then install the caveman (in project scope)

## To remove skills
npx skills remove (interactive selection, best)

### Context7 plugin
- /plugin, select context7 and install it in project, and ask claude to fetch latest docs etc for a particular topic.

### plugins
- agent-skills@addy-agent-skills
- https://skills.addy.ie/tutorials/
- plugins are in one common place and we can enable it per project. Its much better than copying using npx skills. A plugin often contains a bunch of skills and so its easier to disable/enable them.

## Install project wise 
- Avoid cluttering the user space with loads of skills.
- Install whatever you require in a project.
