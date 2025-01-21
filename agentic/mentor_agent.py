from Chain import ReACT, Model
from Curator import Curate
from functools import partial


# ReACT parameters
input = "A topic suggestion."
output = "A curated list of LinkedIn Learning courses providing an end-to-end understanding of the topic."
model = Model("gpt")


# Our tools functions
def find_similar_courses(topic: str) -> list[str]:
    """
    Ask the librarian for courses that are most similar to a search string.
    """
    suggestions = Curate(topic)
    suggestions = [suggestion[0] for suggestion in suggestions]
    return suggestions


def get_second_opinion(topic: str) -> str:
    """
    Ask an L&D admin to review the list of courses.
    """
    pass


def learner_review(topic: str) -> str:
    """
    Ask a learner to watch all the courses and provide feedback.
    """
    pass


# MentorAgent = ReACT(input, output, model)
