from Chain import Prompt, Model, Chain
from review_certificates import review_curriculum, learner_progression, create_curriculum_text_for_review
from Mentor import Mentor


react_prompt = """
You are an AI agent tasked with improving a curriculum curation for a skill-based learning program. 
Your goal is to analyze the current curation, consider the critique provided, and make improvements 
by potentially adding, removing, or replacing courses.

Here is the current curation object:
<curation_object>
{{CURATION_OBJECT}}
</curation_object>

Here is the current curriculum (detailed table of contents for each course):
<curriculum>
{{CURRICULUM}}
</curriculum>

Here is a critique of the current curation:
<critique>
{{CRITIQUE}}
</critique>

You have access to the following function:

Get_alternative_courses(description: str) -> List[str]
This function takes a brief description (1-2 sentences) of desired course content and returns a list
of 5 alternative course titles with their table of contents.

To improve the curation, follow these steps using the ReACT framework:

1. Thought: Analyze the current curation, curriculum, and critique. Identify areas for improvement.
2. Action: Decide on a course of action (e.g., remove a course, add a new course, replace a course).
3. Function Call: If adding or replacing a course, use the Get_alternative_courses function to find 
options.
4. Observation: Review the results of the function call.
5. Repeat steps 1-4 as needed until you have made all necessary improvements.

For each step, use the following format:
<thought>Your thought process</thought>
<action>Your chosen action</action>
<function_call>Get_alternative_courses(description="Your description")</function_call>
<observation>Results of the function call</observation>

Once you have finished improving the curation, provide your final output in this format:
<improved_curation>
{
  "topic": "Updated topic if changed",
  "course_titles": [
    "Updated list of course titles"
  ]
}
</improved_curation>
<explanation>
Briefly explain the changes you made and why they improve the curation based on the critique and 
your analysis.
</explanation>
"""

"""
We need to parse the response to grab "<improved_curation>" or "Get_alternative_courses".

ReACT is not quite right here, how we define the fuction.

"""

if __name__ == "__main__":
    topic = "Data Science with Python"
    print("Generating curriculum for", topic)
    c = Mentor(topic)
    print("Reviewing curriculum for", topic)
    critique = review_curriculum(c, "Data Scientists")
    print("\n=========\ncritique\n=========\n", critique)
    curriculum = create_curriculum_text_for_review(c)
    print("\n=========\ncurriculum\n=========\n", curriculum)
    m = Model('gpt')
    p = Prompt(react_prompt)
    chain = Chain(p, m)
    response = chain.run(input_variables = {'topic': topic, 'curation': c, 'critique': critique})
    print("\n=========\nresponse\n=========\n", response.content)
