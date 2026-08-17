i explore below approaches broadly.
- cron based + claude
    - Neat, simple, but not sure how effective it is for large repos.
    - Also, it depends if my machine is turned on or not.
    - the claude --bg isn't easy to use. Sometimes it is dangling for permissions. 
- claude "/schedule" ( it requires me to add github connector to claude )
    - This is promising. I would say if org allows it, go for this one.
    - Works only with claude
- github workflow - possible, but didn't work due to my free tier. Mostly this will work in paid tiers.
    - it has a separate cli, `gh aw` (aw stands for agentic workflow)
    - https://github.com/kaushik912/agentics.git (forked one)
    - Definitely worth a try in paid tier.
- claude + /loop also can be explored. but again its pertaining to the session (not very useful)

