"""
This script builds a prompt flow over Curator.

Three personas are leveraged:
- an L&D specialist who designs an ideal curriculum for a given topic
- a Curriculum Structuring Specialist who turns that into a structured object
- a Course Librarian who is provided with the RAG (output of Curator queries) and designs a Curation object.
"""

from mentor.mentor.CurriculumModule import Curriculum
from mentor.curator.curate_client import query_server
from conduit.sync import Model, Conduit, Response, ConduitCache, Verbosity
from conduit.parser.parser import Parser
from conduit.prompt.prompt_loader import PromptLoader
from kramer.courses.Get import Get
from kramer.courses.Curation import Curation
from pathlib import Path


# Configs
# ------------------------------------------------
Model.conduit_cache = ConduitCache(name="mentor")
PREFERRED_MODEL = "gpt"
VERBOSITY = Verbosity.COMPLETE
PROMPT_DIR = Path(__file__).parent / "prompts"
PROMPT_LOADER = PromptLoader(PROMPT_DIR)


def lnd_curriculum(topic: str) -> str:
    """
    We have an L&D professional dream up an ideal curriculum.
    Returns a string.
    """
    prompt = PROMPT_LOADER["persona_lnd"]
    model = Model(PREFERRED_MODEL)
    conduit = Conduit(prompt=prompt, model=model)
    response = conduit.run(input_variables={"topic": topic})
    assert isinstance(response, Response), f"Expected Response, got {type(response)}"
    # Extract the answer from between the XML tags
    response_content = str(response.content)
    start = response_content.find("<curriculum_description>") + len(
        "<curriculum_description>"
    )
    end = response_content.find("</curriculum_description>")
    return response_content[start:end]


def curriculum_specialist_curriculum(ideal_curriculum: str, topic: str) -> Curriculum:
    """
    We have a Curriculum Specialist dream up an ideal curriculum.
    Interprets the L&D professional's suggestions into a curriculum object.
    """
    prompt = PROMPT_LOADER["persona_curriculum_specialist"]
    model = Model(PREFERRED_MODEL)
    parser = Parser(Curriculum)
    conduit = Conduit(prompt=prompt, model=model, parser=parser)
    response = conduit.run(
        input_variables={"ideal_curriculum": ideal_curriculum, "topic": topic},
    )
    assert isinstance(response, Response), f"Expected Response, got {type(response)}"
    assert isinstance(response.content, Curriculum), (
        f"Expected Curriculum, got {type(response.content)}"
    )
    return response.content


def identify_courses(curriculum: Curriculum) -> Curation:
    """
    We have a Curriculum Specialist identify the courses that best fit the ideal curriculum.
    Returns a Curation object.
    """
    recommended_courses = []
    for module in curriculum.modules:
        # Assemble a query for this module
        query_string = (
            module.title
            + ": "
            + module.description
            + "\nLearning Objectives:\n"
            + "\n\t".join(module.learning_objectives)
        )
        # RAG: get the top 10 courses for this module
        course_matches = query_server(query_string=query_string)
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
    # Our chain
    model = Model(PREFERRED_MODEL)
    prompt = PROMPT_LOADER["persona_video_course_librarian"]
    parser = Parser(Curation)  # Librarian returns a neutered Curation object
    conduit = Conduit(prompt=prompt, model=model, parser=parser)
    response = conduit.run(
        input_variables={
            "topic": curriculum.topic,
            "curriculum": curriculum,
            "courses": course_context,
        },
    )
    assert isinstance(response, Response), f"Expected Response, got {type(response)}"
    assert isinstance(response.content, Curation), (
        f"Expected Curation, got {type(response.content)}"
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


topic = "Data Science"
desc = lnd_curriculum(topic)
curriculum = curriculum_specialist_curriculum(desc, topic)
curation = identify_courses(curriculum)
print(curation)
exit()


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
