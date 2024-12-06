AI Agent:

1. Its a software component that can do a task on its own.
2. It does it using LLM intelligence and a set of Tools which we provide it.

- When a user assigns a task to an agent, it'll use LLM as a "Reasoning" engine.
- It'll take the task, reason and see which tools are available on hand to accomplish this particular task.
- Then it'll take an action using the tool from the tool list which we provide.
- Get the response, it'll not straight-away use that response , it'll observe the response.
- if it's happy with the response, it'll use it to generate a final response.
- If it's not happy, it'll continue the cycle of "reasoning".
- It will once again see if it can use the same tool previously to get one more response or it has to use a completely differnet tool to get the task done.
- Finally, it's happy with the response ,it'll use the response to generate the final response.

Most of the LLMs support *Agents*.



