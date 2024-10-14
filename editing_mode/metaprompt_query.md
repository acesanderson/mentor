Metaprompt task:

I have an LLM application that takes a description of a skill and uses it to come up with a curriculum.
It then uses a RAG architecture to assign courses from my company's video library (10,000+ courses) to that curriculum.
The quality of it is quite variable, and I want to run it through a series of evaluations and have an agentic LLM improve the quality of the curation using a few functions. I am new to agentic AI so let's just use the ReACT framework for a start.

Context:
- I will give this agent the following:
 - a Curation object (rendered as json in the prompt)
{
  "topic": "Data Visualization and Reporting for Financial Analysis",
  "course_titles": [
    "Excel for Financial Planning and Analysis (FP&A)",
    "Advanced Power BI: DAX Language, Formulas, and Calculations",
    "Advanced Data Visualizations: 10 Uncommon Plot Types and How to Use Them",
    "Corporate Financial Statement Analysis"
  ]
}
 - a curriculum (this is a lot of text: it's the verbose TOCs for each of the courses in course_titles)
- a critique (provided by one of my other LLMs)

The agent has access to the following functions:
Get_alternative_courses: the LLM can provide a description (a couple sentences is best) to this function, and it returns five matches. These are rendered as course titles and their tocs.

I would like the llm agent to be able to reflect on the critique and what it means for amending the curriculum. This might involve removing courses from the course list, replacing courses on the course list, or adding new courses that map to a better-structured curriculum.

Give me a ReACT-style prompt that will guide an LLM agent to return a higher-quality Curation object.