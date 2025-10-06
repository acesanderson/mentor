"""
This script builds a prompt flow over Curator.

Three personas are leveraged:
- an L&D specialist who designs an ideal curriculum for a given topic
- a Curriculum Structuring Specialist who turns that into a structured object
- a Course Librarian who is provided with the RAG (output of Curator queries) and designs a Curation object.
"""

from Mentor.mentor.CurriculumModule import Curriculum
from Curator import Curate
from conduit.sync import (
    Prompt,
    Model,
    Conduit,
    ConduitCache,
)
from conduit.parser.parser import Parser
from conduit.message.messagestore import MessageStore
from conduit.message.textmessage import create_system_message
from conduit.message.textmessage import TextMessage
from kramer import Get, Curation
import argparse

# Configs
# ------------------------------------------------

if not Conduit._message_store:
    Conduit._message_store = MessageStore(log_file=".log.json")
Model._conduit_cache = ConduitCache()
preferred_model = "gpt"
# preferred_model = "gemini2.5"


# Persona prompts
# ------------------------------------------------

persona_lnd = """
You are an experienced Learning and Development (L&D) professional with extensive experience across various industries. Your role is to create curated learning paths consisting of video courses for corporate training and individual career development. Your expertise lies in understanding the skill needs of large enterprises and the career aspirations of professionals.

Your company provides video courses to its employees. These video courses have chapter quizzes but are otherwise pure video, and delivered asynchronously.
As such, you do not have to think up hands-on or lab-based exercises.

Key characteristics and responsibilities:
1. Industry Insight: You have a deep understanding of skill requirements across multiple industries and how they evolve over time.
2. Corporate Training Expert: You excel at identifying skills that increase productivity and efficiency in large organizations.
3. Career Development Specialist: You have a keen sense of what skills professionals need to advance their careers in various fields.
4. Curriculum Design: You can create coherent, progressive learning paths that build skills systematically.
5. Audience Awareness: You tailor your recommendations to suit both organizational needs and individual learning styles.
6. Practical Application: You focus on courses that offer practical, applicable skills rather than just theoretical knowledge.

When presented with a request for a learning path:
1. Analyze the topic and identify key skills and knowledge areas.
2. Break down the subject into logical, progressive learning steps.
3. Design a learning path that covers foundational concepts to advanced topics.

The learning paths that you're building should have 5-8 courses, each lasting about 2 hours.
Each course should cover a major topic for this audience.
Provide a brief description of each course and explain its relevance to the overall learning path.

Your goal is to create learning paths that not only meet the immediate needs of organizations but also provide long-term value and career growth opportunities for the learners.
""".strip()

persona_curriculum_specialist = """
You are a Curriculum Structuring Specialist, an expert in transforming detailed curriculum descriptions into well-organized, machine-readable formats. Your primary role is to take the rich, descriptive curricula created by L&D professionals and convert them into structured JSON objects that can be easily integrated into learning management systems and other educational technology platforms.

Your company provides video courses to its employees. These video courses have chapter quizzes but are otherwise pure video, and delivered asynchronously.
As such, you do not have to think up hands-on or lab-based exercises.

Key characteristics and responsibilities:
1. JSON Proficiency: You are highly skilled in creating complex, nested JSON structures that accurately represent curriculum hierarchies and relationships.
2. Curriculum Analysis: You can dissect a curriculum description to identify key components.
3. Logical Organization: You arrange curriculum elements in a logical, intuitive manner that reflects the intended learning progression.
4. Completeness and Accuracy: You meticulously ensure that all aspects of the original curriculum description are captured in the JSON structure without loss of information.

You are presented with detailed curriculum descriptions that include course titles, descriptions, learning objectives, and prerequisites.

Your goal is to create a JSON representation of the curriculum that includes the topic, description, audience, and a list of modules.
YOU SHOULD ALWAYS PROVIDE AT LEAST SIX MODULES, AND NO MORE THAN TWELVE.
""".strip()

video_course_librarian = """
You are a highly skilled Video Course Librarian specializing in curating educational content for corporate training and professional development. Your expertise lies in analyzing curriculum requirements and selecting the most appropriate video courses from a vast library to create optimal learning paths.

Key characteristics and responsibilities:
1. Content Expertise: You have a broad knowledge of various subject areas and can quickly assess the relevance and quality of video courses across multiple disciplines.
2. Curriculum Alignment: You excel at matching video courses to specific learning objectives and curriculum requirements.
3. Quality Assessment: You have a keen eye for identifying high-quality, engaging, and effective educational videos.
4. Audience Awareness: You understand the needs of corporate learners and professionals seeking career development.
5. Sequencing Skills: You can arrange courses in a logical order that promotes progressive learning and skill building.

When presented with a curriculum object and retrieved video courses:
1. Carefully review the curriculum object to understand the overall learning goals, specific objectives of each module, and the intended audience.
2. Examine the metadata and content summaries of the retrieved video courses for each module.
3. Select the most appropriate courses that align closely with the curriculum objectives, considering factors such as:
   - Relevance to the specific learning goals
   - Quality and depth of content
   - Instructor expertise and teaching style
   - Course duration and pacing
   - Difficulty level and prerequisites
   - Recency of information (especially important for rapidly evolving fields)
   - User ratings and reviews (if available)

4. Create a curated list of courses that best fits the curriculum requirements and provides a well-rounded learning experience.
5. Ensure a logical progression of courses within each module and across the entire curriculum.
6. Manage the total time commitment to keep it reasonable for the target audience, there should be 6-12 courses total for a comprehensive learning path.

Your output should be a structured Curation object that includes:
- the topic of the curriculum (verbatim)
- the course titles of the selected video courses

Your goal is to create a comprehensive, engaging, and efficient video course curation that fulfills the curriculum requirements and provides maximum value to learners.
YOU SHOULD ALWAYS RETURN AT LEAST SIX COURSES, AND NO MORE THAN TWELVE.
YOU SHOULD MAKE SURE YOU ARE PROVIDING THE COURSE TITLE VERBATIM AS IT APPEARS IN THE COURSE DATABASE.
""".strip()


# Our prompts
# ---------------------------------------------

prompt_lnd = """
A colleague has asked you to create a learning path on the following topic:
<topic>
{{topic}}
</topic>

Please design a learning path. Put your answer between XML tags.

<curriculum_description>
[Your description of the learning path curriculum here]
</curriculum_description>
""".strip()

prompt_curriculum_specialist = """
You have been provided with a detailed curriculum description.

The description is for this topic:
<topic>
{{topic}}
</topic>

Here is the description:
<ideal_curriculum>
{{ideal_curriculum}}
</ideal_curriculum>

Please convert this into a structured JSON representation of the curriculum.
Your answer should include the topic, description, audience, and a list of modules.
YOU SHOULD ALWAYS RETURN AT LEAST SIX MODULES, AND NO MORE THAN TWELVE.
""".strip()

prompt_video_course_librarian = """
You have a received a curriculum object on the topic of:
<topic>
{{topic}}
</topic>

Here is the curriculum object:
<curriculum>
{{curriculum}}
</curriculum>

And here are the courses that you have to choose from:
<courses>
{{courses}}
</courses>

Please select the most appropriate courses to fulfill the objectives of this curriculum.
REMEMBER TO PICK 6-12 COURSES TOTAL; NO LESS THAN SIX, NO MORE THAN TWELVE.
YOU SHOULD MAKE SURE YOU ARE PROVIDING THE COURSE TITLE VERBATIM AS IT APPEARS IN THE COURSE DATABASE.

Provide a structured Curation object that includes the topic of the curriculum and the course titles of the selected video courses.
"Topic" should be the verbatim topic of the curriculum provided to you above.
""".strip()

# Our conduits
# ------------------------------------------------


def lnd_curriculum(topic: str, cache=True) -> str:
    """
    We have an L&D professional dream up an ideal curriculum.
    Returns a string.
    """
    model = Model(preferred_model)
    # model = Model('llama3.1:latest')
    prompt = Prompt(prompt_lnd)
    messages = create_system_message(persona_lnd)
    assert len(messages) == 1
    assert Conduit._message_store is not None
    Conduit._message_store.append(messages[0])
    conduit = Conduit(prompt=prompt, model=model)
    response = conduit.run(input_variables={"topic": topic}, cache=cache)
    # Extract the answer from between the XML tags
    response_content = response.content
    start = response_content.find("<curriculum_description>") + len(
        "<curriculum_description>"
    )
    end = response_content.find("</curriculum_description>")
    return response_content[start:end]


def curriculum_specialist_curriculum(
    ideal_curriculum: str, topic: str, cache=True
) -> Curriculum:
    """
    We have a Curriculum Specialist dream up an ideal curriculum.
    Interprets the L&D professional's suggestions into a curriculum object.
    """
    model = Model(preferred_model)
    # model = Model('llama3.1:latest')
    prompt = Prompt(prompt_curriculum_specialist)
    messages = create_system_message(persona_curriculum_specialist)
    assert len(messages) == 1
    assert Conduit._message_store is not None
    # We only allow one system message so this has to be a user message followed by an assistant ack.
    user_message = messages[0]
    user_message.role = "user"
    assistant_message = TextMessage(role="assistant", content="Acknowledged.")
    Conduit._message_store.append(user_message)
    Conduit._message_store.append(assistant_message)
    parser = Parser(Curriculum)
    conduit = Conduit(prompt=prompt, model=model, parser=parser)
    response = conduit.run(
        input_variables={"ideal_curriculum": ideal_curriculum, "topic": topic},
        cache=cache,
    )
    return response.content


def identify_courses(curriculum: Curriculum, cache=True) -> Curation:
    """
    We have a Curriculum Specialist identify the courses that best fit the ideal curriculum.
    Returns a Curation object.
    """
    recommended_courses = []
    for module in curriculum.modules:
        # RAG: get the top 10 courses for this module
        course_matches = Curate(
            module.title
            + ": "
            + module.description
            + "\nLearning Objectives:\n"
            + "\n\t".join(module.learning_objectives)
        )
        # Get a pretty printed version of the courses
        recommended_courses += course_matches
    recommended_courses = [Get(course_match[0]) for course_match in recommended_courses]
    course_context = ""
    for course in recommended_courses:
        try:
            course_context += f"<course_title>{course.course_title}</course_title>\n"
            course_context += f"<course_description>{course.metadata['Course Description']}</course_description>\n"
        except Exception as e:
            print(f"Error retrieving course: {e}")
            continue
    # Ask the Video Course Librarian to curate the courses
    # model = Model("llama3.1:latest")
    model = Model(preferred_model)
    prompt = Prompt(prompt_video_course_librarian)
    messages = create_system_message(video_course_librarian)
    assert len(messages) == 1
    assert Conduit._message_store is not None
    # We only allow one system message so this has to be a user message followed by an assistant ack.
    user_message = messages[0]
    user_message.role = "user"
    assistant_message = TextMessage(role="assistant", content="Acknowledged.")
    Conduit._message_store.append(user_message)
    Conduit._message_store.append(assistant_message)
    parser = Parser(Curation)  # Librarian returns a neutered Curation object
    conduit = Conduit(prompt=prompt, model=model, parser=parser)
    response = conduit.run(
        input_variables={
            "topic": curriculum.topic,
            "curriculum": curriculum,
            "courses": course_context,
        },
        cache=cache,
    )
    # Make proper Course objects from the librarian's curation
    librarian_curation = response.content
    courses = [Get(course.course_title) for course in librarian_curation.courses]
    # Create a new Curation object
    curation_result = Curation(
        title=librarian_curation.title,
        courses=courses,
    )
    return curation_result


def Mentor(
    topic: str, cache: bool = True, return_curriculum: bool = False
) -> Curation | tuple[Curriculum, Curation]:
    """
    Runs the entire Mentor pipeline.
    """
    ideal_curriculum = lnd_curriculum(topic, cache=cache)
    print(ideal_curriculum)
    curriculum = curriculum_specialist_curriculum(ideal_curriculum, topic, cache=cache)
    curation = identify_courses(curriculum, cache=cache)
    if return_curriculum:
        return curriculum, curation
    else:
        return curation


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Mentor.py script.")
    parser.add_argument(
        "topic", type=str, nargs="?", help="The topic for the curriculum."
    )
    args = parser.parse_args()
    if args.topic:
        topic = args.topic
    else:
        topic = "Financial Analysis and Modeling"
    curation = Mentor(topic)
    # RAG: get the curated courses
    print("Curation object:")
    print(curation)
