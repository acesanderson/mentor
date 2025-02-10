from Chain import ReACT, Model, Parser
from Curator import Curate
from Mentor import (
    review_curriculum,
    learner_progression,
)
from Kramer import Curation, Get


# ReACT parameters
input = "A topic suggestion."
output = "A curated list of LinkedIn Learning courses providing an end-to-end understanding of the topic."
model = Model("gpt")


# Our tools functions
def find_similar_courses(topic: str) -> list[str]:
    """
    Ask the librarian for courses that are most similar to a search string.
    """
    suggestions = Curate(topic, n_results=50, k=15)
    suggestions = [suggestion[0] for suggestion in suggestions]
    return suggestions


def get_second_opinion(curation_title: str, curation: list[str], audience: str) -> str:
    """
    Ask an L&D admin to review the list of courses. Curation should be a list of strings.
    """
    courses = [Get(course) for course in curation]
    if any(course is None for course in courses):
        return (
            "Some courses could not be found. Please provide a valid list of courses."
        )
    curation_object = Curation(title=curation_title, courses=courses)
    review = review_curriculum(curation_object, audience)
    return review


def learner_review(curation_title: str, curation: list[str], audience: str) -> str:
    """
    Ask a learner to watch all the courses and provide feedback. Curation should be a list of strings.
    """
    courses = [Get(course) for course in curation]
    if any(course is None for course in courses):
        return (
            "Some courses could not be found. Please provide a valid list of courses."
        )
    curation_object = Curation(title=curation_title, courses=courses)
    review = learner_progression(curation_object, audience)
    return review


if __name__ == "__main__":
    model = Model("o3-mini")
    MentorAgent = ReACT(
        input,
        output,
        tools=[find_similar_courses, get_second_opinion, learner_review],
        model=model,
        log_file="mentor_agent.log",
    )
    MentorAgent.query("Python for Business Analysts")
