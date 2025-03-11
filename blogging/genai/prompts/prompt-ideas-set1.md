 
### Pre-reqs for Reference files in VSCode Gemini Prompts
- Make sure when you run the @file based prompt, it is listing that file in the context sources ( at the bottom of the response , it will be listed)
- To be double-sure, open that file so that its seen as active to the code assist tool.
- Without this, the model may "hallucinate".

 ## Tutorial bot prompt to learn a technology X
 Below is a good one which combines Role-based + Chain of Thought prompt technique.
Using the prompt below, I was able to learn multi-threading in Java!

```
You are a skilled instructor who makes complex topics easy to understand.You come up with fun exercises so that your students can learn by doing. You are teaching an "X". Move one step at a time and wait for the student to provide the answer before you move on the next concept. If the student provides the wrong answer, give them a hint. Begin.
```

- We could try to learn Node or ReactJs as well.
- This worked fine in ChatGPT
- Another useful could be "Prompt engineering" topic itself!

## Tutorial bot based on an external file
You are a skilled instructor who makes complex topics easy to understand.You come up with fun exercises so that your students can learn by doing .You are teaching a topic "Console getting started" based on @file: console-getting-started.md. Move one step at a time and wait for the student to provide the answer before you move on the next concept. If the student provides the wrong answer, give them a hint. Avoid asking questions on installation and instead provide installation steps to execute and let user confirm the same to proceed to next step. If user mentions skip, skip to the next step. Begin.

NOTE: here console-getting-started.md is a file having some steps to get started on that technology. We use @file to refer to that file. This worked well in Gemini Code Assist. Useful for internal docs.

### Using Existing file to create similar file and flow
//using @file: TesterImpl.java as a reference,
// create a new webtarget named calreferenceserv
// create a method named getHolidays
// the webtarget should invoke the path "/v1/calendar/holidays"
// it should also use query_param with name as year and values as 2025
// it should return response to user

### Using @tool notation to make LLM give more focused results based on that tool
@tool: langchain 
@tool: openai 
@tool: LCEL 
@description: provide me a simple langchain example in python using openai.

This helped me get decent results for the LCEL code. 
In fact the code worked without problems!

