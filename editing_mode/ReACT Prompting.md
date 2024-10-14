[[Berkeley MOOC - Week 2 - LLM agents, brief history and overview]]

***What ReACT Does Differently:***

- ***Reasoning Traces:** ReACT prompts encourage the LLM to generate a sequence of steps explaining its thought process along with the final answer. This reasoning trace provides insights into how the LLM arrived at its conclusion.*
- ***Action Integration:** ReACT allows the LLM to interact with external information sources like databases or knowledge graphs during the reasoning process. This can help the LLM access and incorporate factual information from the real world, improving the accuracy and reliability of its responses.*

![[Pasted image 20240922210206.png]]

### Clever way to test ReACT prompting

![[Pasted image 20240922210902.png|450]]

### Fine Tuning options
https://pub.towardsai.net/finetuning-llms-for-react-9ab291d84ddc

### Write up

https://www.promptingguide.ai/techniques/react

### Example


```
Question: How do I prepare a healthy meal?

ReAct Prompting Sequence:

Thought 1: Consider what constitutes a balanced meal, including protein, vegetables, and whole grains. Act 1: Identify[ingredients for a balanced meal] Obs 1: Lean proteins, a variety of colorful vegetables, and whole grains are staples of a nutritious meal.

Thought 2: Decide on a cooking method that preserves nutrients and avoids excessive fats, such as grilling or steaming. Act 2: Select[healthy cooking methods] Obs 2: Cooking methods like steaming vegetables and grilling chicken are healthier and maintain more of the food's nutritional value.

Thought 3: Plan when to cook so that the meal can be enjoyed fresh, without resorting to processed or fast food options. Act 3: Schedule[meal preparation time] Obs 3: Preparing meals after work or on weekends can make it easier to avoid unhealthy convenience foods.

Outcome: By choosing fresh, wholesome ingredients, using cooking methods that maintain nutritional value, and scheduling a regular time to prepare meals, you can enjoy healthy, homemade meals consistently.
```

[Mastering ReACT Prompting](https://blog.gopenai.com/mastering-react-prompting-a-crucial-step-in-langchain-implementation-a-guided-example-for-agents-efdf1b756105)

![[Pasted image 20240531212437.png]]

### Zero-shot

```
## Print template used by LangChain  
print(react.agent.llm_chain.prompt.template)
```

```
Question: What is the elevation range for the area that the eastern sector of the Colorado orogeny extends into?  
Thought: I need to search Colorado orogeny, find the area that the eastern sector of the Colorado orogeny extends into, then find the elevation range of the area.  
Action: Search[Colorado orogeny]  
Observation: The Colorado orogeny was an episode of mountain building (an orogeny) in Colorado and surrounding areas.  
Thought: It does not mention the eastern sector. So I need to look up eastern sector.  
Action: Lookup[eastern sector]  
Observation: (Result 1 / 1) The eastern sector extends into the High Plains and is called the Central Plains orogeny.  
Thought: The eastern sector of Colorado orogeny extends into the High Plains. So I need to search High Plains and find its elevation range.  
Action: Search[High Plains]  
Observation: High Plains refers to one of two distinct land regions  
Thought: I need to instead search High Plains (United States).  
Action: Search[High Plains (United States)]  
Observation: The High Plains are a subregion of the Great Plains. From east to west, the High Plains rise in elevation from around 1,800 to 7,000 ft (550 to 2,130 m).[3]  
Thought: High Plains rise in elevation from around 1,800 to 7,000 ft, so the answer is 1,800 to 7,000 ft.  
Action: Finish[1,800 to 7,000 ft]  
  
Question: Musician and satirist Allie Goertz wrote a song about the "The Simpsons" character Milhouse, who Matt Groening named after who?  
Thought: The question simplifies to "The Simpsons" character Milhouse is named after who. I only need to search Milhouse and find who it is named after.  
Action: Search[Milhouse]  
Observation: Milhouse Mussolini Van Houten is a recurring character in the Fox animated television series The Simpsons voiced by Pamela Hayden and created by Matt Groening.  
Thought: The paragraph does not tell who Milhouse is named after, maybe I can look up "named after".  
Action: Lookup[named after]  
Observation: (Result 1 / 1) Milhouse was named after U.S. president Richard Nixon, whose middle name was Milhous.  
Thought: Milhouse was named after U.S. president Richard Nixon, so the answer is Richard Nixon.  
Action: Finish[Richard Nixon]  
  
Question: Which documentary is about Finnish rock groups, Adam Clayton Powell or The Saimaa Gesture?  
Thought: I need to search Adam Clayton Powell and The Saimaa Gesture, and find which documentary is about Finnish rock groups.  
Action: Search[Adam Clayton Powell]  
Observation: Could not find [Adam Clayton Powell]. Similar: [’Adam Clayton Powell III’, ’Seventh Avenue (Manhattan)’, ’Adam Clayton Powell Jr. State Office Building’, ’Isabel Washington Powell’, ’Adam Powell’, ’Adam Clayton Powell (film)’, ’Giancarlo Esposito’].  
Thought: To find the documentary, I can search Adam Clayton Powell (film).  
Action: Search[Adam Clayton Powell (film)]  
Observation: Adam Clayton Powell is a 1989 American documentary film directed by Richard Kilberg. The film is about the rise and fall of influential African-American politician Adam Clayton Powell Jr.[3][4] It was later aired as part of the PBS series The American Experience.  
Thought: Adam Clayton Powell (film) is a documentary about an African-American politician, not Finnish rock groups. So the documentary about Finnish rock groups must instead be The Saimaa Gesture.  
Action: Finish[The Saimaa Gesture]  
  
Question: What profession does Nicholas Ray and Elia Kazan have in common?  
Thought: I need to search Nicholas Ray and Elia Kazan, find their professions, then find the profession they have in common.  
Action: Search[Nicholas Ray]  
Observation: Nicholas Ray (born Raymond Nicholas Kienzle Jr., August 7, 1911 - June 16, 1979) was an American film director, screenwriter, and actor best known for the 1955 film Rebel Without a Cause.  
Thought: Professions of Nicholas Ray are director, screenwriter, and actor. I need to search Elia Kazan next and find his professions.  
Action: Search[Elia Kazan]  
Observation: Elia Kazan was an American film and theatre director, producer, screenwriter and actor.  
Thought: Professions of Elia Kazan are director, producer, screenwriter, and actor. So profession Nicholas Ray and Elia Kazan have in common is director, screenwriter, and actor.  
Action: Finish[director, screenwriter, actor]  
  
Question: Which magazine was started first Arthur’s Magazine or First for Women?  
Thought: I need to search Arthur’s Magazine and First for Women, and find which was started first.  
Action: Search[Arthur’s Magazine]  
Observation: Arthur’s Magazine (1844-1846) was an American literary periodical published in Philadelphia in the 19th century.  
Thought: Arthur’s Magazine was started in 1844. I need to search First for Women next.  
Action: Search[First for Women]  
Observation: First for Women is a woman’s magazine published by Bauer Media Group in the USA.[1] The magazine was started in 1989.  
Thought: First for Women was started in 1989. 1844 (Arthur’s Magazine) < 1989 (First for Women), so Arthur’s Magazine was started first.  
Action: Finish[Arthur’s Magazine]  
  
Question: Were Pavel Urysohn and Leonid Levin known for the same type of work?  
Thought: I need to search Pavel Urysohn and Leonid Levin, find their types of work, then find if they are the same.  
Action: Search[Pavel Urysohn]  
Observation: Pavel Samuilovich Urysohn (February 3, 1898 - August 17, 1924) was a Soviet mathematician who is best known for his contributions in dimension theory.  
Thought: Pavel Urysohn is a mathematician. I need to search Leonid Levin next and find its type of work.  
Action: Search[Leonid Levin]  
Observation: Leonid Anatolievich Levin is a Soviet-American mathematician and computer scientist.  
Thought: Leonid Levin is a mathematician and computer scientist. So Pavel Urysohn and Leonid Levin have the same type of work.  
Action: Finish[yes]  
  
  
Question: {input}  
{agent_scratchpad}
```


