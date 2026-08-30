# My notes:
- Here, client makes a request to create an app.
- First it goes to Orchestrator
    - it saves the app details from request and initializes state to `APP_INITIATED`
    - post commit, then it publishes a command (`cmd.createGitRepo`)` to Command-Exchange.
    - Command-exchange is mapped to a queue by this routing key: `cmd.createGitRepo`, so message goes to that queue.
        - Worker (aka. WorkerCommandListener) picks up this message and does some processing
        - Post that, it publishes a "event" gitRepoCreated to the Event-Queue. 
- OrchestratorListener listens to this event and calls the next corresponding Orchestrator method.
    - It does 2 state transitions: 
        - one from APP_INITIATED to GIT_REPO_CREATED
        - second from GIT_REPO_CREATED to REGISTERING
    - Then save the state in the DB
    - Only post commit, it publishes the next command : cmd.registerApp
    - The process continues..
    - For clarity, we are also auditing the state changes in a separate table.

# Key point 
 - In this design, 
    - The worker doesn't do any state updates. It reads commands from queue and publishes events (based on success/failure)
    - The orchestrator solely does the state transitions and updates.

# Follow-up (Optional)
- What if we want to have multiple states?. How can we make this state transitions more configurable? 
- Some of the steps in orchestrator are generic. 
    - It reads message from event-exchange and updates state in DB (confirming receipt of previous command's status)
    - Based on status, it picks the next command, updates again the state with new-command, and publishes message to command-exchange. 
    - We also need to track success/failure properly to handle retries.
