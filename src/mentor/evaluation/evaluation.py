"""
Adapted from the original review_certificates script from old Course project.
"""

from kramer.courses.Curation import Curation
from kramer.courses.Course import Course
from conduit.sync import Prompt, Model, Conduit, Response
from pathlib import Path


# Path
dir_path = Path(__file__).parent
# Our prompts: we have five
prompts = "prompts"
with open(dir_path / prompts / "curriculum_review.jinja", "r") as f:
    curriculum_review_prompt_string = f.read()
with open(dir_path / prompts / "learner_progression_prompt.jinja", "r") as f:
    learner_progression_prompt_string = f.read()
with open(dir_path / prompts / "audience_prompt.jinja", "r") as f:
    audience_prompt_string = f.read()
with open(dir_path / prompts / "title_prompt.jinja", "r") as f:
    title_prompt_string = f.read()
with open(dir_path / prompts / "query_prompt.jinja", "r") as f:
    query_prompt_string = f.read()


# Our conduits
def review_curriculum(curation: Curation, audience: str, model=Model("claude")) -> str:
    """
    This is a generic review prompt. Grain of salt on results.
    Prompt takes curation and audience as input variables.
    """
    prompt = Prompt(curriculum_review_prompt_string)
    conduit = Conduit(prompt=prompt, model=model)
    response = conduit.run(
        input_variables={"curriculum": curation.snapshot, "audience": audience}
    )
    assert isinstance(response, Response), "Response is not of type Response"
    return str(response.content)


def learner_progression(
    curation: Curation, audience: str, model=Model("llama3.1:latest")
) -> str:
    """
    Takes a curation object and returns a review from the perspective of target audience going course by course.
    Prompt takes curation and audience as input variables.
    """
    prompt = Prompt(learner_progression_prompt_string)
    conduit = Conduit(prompt=prompt, model=model)
    response = conduit.run(
        input_variables={"curriculum": curation.TOCs, "audience": audience}
    )
    assert isinstance(response, Response), "Response is not of type Response"
    return str(response.content)


def classify_audience(
    curation: Curation | Course | str, model=Model("llama3.1:latest")
) -> str:
    """
    Takes a curation object and returns a classification of the audience.
    """
    prompt = Prompt(audience_prompt_string)
    conduit = Conduit(prompt=prompt, model=model)
    if isinstance(curation, str):
        response = conduit.run(input_variables={"curriculum": curation})
    elif isinstance(curation, Curation):
        response = conduit.run(input_variables={"curriculum": curation.snapshot})
    elif isinstance(curation, Course):
        response = conduit.run(
            input_variables={"curriculum": curation.course_TOC_verbose}
        )
    assert isinstance(response, Response), "Response is not of type Response"
    return str(response.content)


def title_certificate(curation: Curation, model=Model("llama3.1:latest")) -> str:
    """
    Takes a curation object and returns a title for the certificate.
    Prompt takes curation and black list (as defined in blacklist.conf) as input variables.
    """
    prompt = Prompt(title_prompt_string)
    conduit = Conduit(prompt=prompt, model=model)
    response = conduit.run(input_variables={"curation": curation.snapshot})
    assert isinstance(response, Response), "Response is not of type Response"
    return str(response.content)
