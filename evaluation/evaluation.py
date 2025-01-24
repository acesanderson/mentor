"""
Adapted from the original review_certificates script from old Course project.
"""

from Kramer import Curation
from Chain import Prompt, Model, Chain
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
# Blacklist
with open(dir_path / "blacklist.conf", "r") as f:
    blacklist = ",".join(f.read().split("\n"))


# Our chains
def review_curriculum(curation: Curation, audience: str, model=Model("claude")) -> str:
    """
    This is a generic review prompt. Grain of salt on results.
    Prompt takes curation and audience as input variables.
    """
    prompt = Prompt(curriculum_review_prompt_string)
    chain = Chain(prompt=prompt, model=model)
    response = chain.run(
        input_variables={"curriculum": curation.snapshot, "audience": audience}
    )
    return response.content


def learner_progression(
    curation: Curation, audience: str, model=Model("llama3.1:latest")
) -> str:
    """
    Takes a curation object and returns a review from the perspective of target audience going course by course.
    Prompt takes curation and audience as input variables.
    """
    prompt = Prompt(learner_progression_prompt_string)
    chain = Chain(prompt=prompt, model=model)
    response = chain.run(
        input_variables={"curriculum": curation.TOCs, "audience": audience}
    )
    return response.content


def classify_audience(curation: Curation, model=Model("llama3.1:latest")) -> str:
    """
    Takes a curation object and returns a classification of the audience.
    """
    prompt = Prompt(audience_prompt_string)
    chain = Chain(prompt=prompt, model=model)
    response = chain.run(input_variables={"curriculum": curation.snapshot})
    return response.content


def title_certificate(curation: Curation, model=Model("llama3.1:latest")) -> str:
    """
    Takes a curation object and returns a title for the certificate.
    Prompt takes curation and black list (as defined in blacklist.conf) as input variables.
    """
    prompt = Prompt(title_prompt_string)
    chain = Chain(prompt=prompt, model=model)
    response = chain.run(
        input_variables={"curriculum": curation.snapshot, "blacklist": blacklist}
    )
    return response.content
