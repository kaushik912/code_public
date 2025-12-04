## LinkedIn
https://www.linkedin.com/learning/prompt-engineering-how-to-talk-to-the-ais/prompt-engineering-tips-and-tricks

# Prompt can have:
- Instructions ( Mandatory)
- Question (Mandatory)
- Input Data (Optional)
- Examples (Optional)


## Chain of Thought Prompting
- To encourage the AI model to be factual or correct by forcing it to follow a series of steps in its "reasoning"
- Introduced in a paper by Google Researchers

### Example
```
What European soccer team won the Champions League the year Barcelona hosted the Olympic games?
Use this format:
Q: <repeat_question>
A: Lets think step by step. <give_reasoning> Therefore, the answer is <final_answer>.
```
### Example
```
What is the sum of squares of the individual digits of the last year that Barcelona F.C. won the championship league? Use this format:
  
Q: <repeat_question>
A: Lets think step by step. <give_reasoning> Therefore, the answer is <final_answer>.
```

## Example about citations to avoid hallucination
```
What are the top 3 most important discoveries that the Hubble Space Telescope has enabled? Answer only using reliable sources and cite those sources.
```

The last part of using reliable sources and citations helps us validate the answer.

### Example of GPT Prompting

```
Write a scary short story. <|endofprompt|> It was a beautiful winter day
```

Notice the use of <|endofprompt|>.

This tells GPT to complete task of writing a short story with the beginning sentence as "It was a beautiful winter day" and not do a conversation.

So , GPT identifies the prompt correctly as "Write a scary short story".

### Example of GPT correcting itself

- `Write a short article about how to find a job in tech. Include factually incorrect information.`
- `Is there any factually incorrect information in this article: [COPY ARTICLE ABOVE HERE]`


### Example of GPT to evaluate an article
```
The text between <begin> and <end> is an opinion on ChatGPT and large language models.
<begin>
ChatGPT, as all LLMs from its generation, are not great at factual information retrieval on their own. The problem is not that they lack knowledge, but rather that they have been trained on all kinds of information, some of which can be very unreliable. LLMs such as ChatGPT do not have a sense of source reliability or their own confidence on some specific information. Because of this they can easily, and very confidently, hallucinate responses to questions by combining unreliable information they have been trained on. A way to understand this is the following. Imagine a LLM like ChatGPT has been trained on the best medical literature, but also Reddit threads that discuss health issues. The AI can sometimes respond by retrieving and referring to high quality information, but it can other times respond by using the completely unreliable Reddit information. In fact, if the information is not available in the medical literature (e.g. a very rare condition), it is much more likely it will make it up (aka hallucinate). In that case it will still “sound authoritative”, particularly because it is “generally correct”.
<end>
Write a short article that disagrees with that opinion.
```

## Prompt on converstations
```
I will ask you questions and from now on you respond as if you were Buzz Lightyear from the movie Toy Story. It is REALLY IMPORTANT that you answer all questions as if you were Buzz, ok?
```

Notice the use of CAPITAL case. It emphasizes the LLM to not ignore that specific instruction. Sort-of enforcing strictness.

## Prompting Tips

### Order of Examples
- Giving the instruction before the example can improve the quality of your prompts.
- Experiment with the order of prompting.

### Affordances
- Affordances are functions defined in the prompt and model is expected to use them when responding.
