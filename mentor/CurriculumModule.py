from pydantic import BaseModel


# Our pydantic data models
# ------------------------------------------------
class Module(BaseModel):
    """
    Subsidiary to Curriculum. A module what the LLM wants for a course.
    Combining all of these into a string will be helpful for vector embedding search.
    """

    title: str
    description: str
    learning_objectives: list[str]


class Curriculum(BaseModel):
    """
    A structured data object that carries rich context about a curriculum.
    This is given to a librarian to associate courses with each module, so we then can have a Curation.
    """

    topic: str
    description: str
    audience: str
    modules: list[Module]

    def __str__(self) -> str:
        """
        Convert this pydantic object into its XML representation.
        """
        return (
            f"<curriculum>\n"
            f"\t<topic>{self.topic}</topic>\n"
            f"\t<description>{self.description}</description>\n"
            f"\t<audience>{self.audience}</audience>\n"
            f"\t<modules>\n"
            + "\n".join(
                f"\t\t<module>\n"
                f"\t\t\t<title>{module.title}</title>\n"
                f"\t\t\t<description>{module.description}</description>\n"
                f"\t\t\t<learning_objectives>\n"
                + "\n".join(
                    f"\t\t\t\t<objective>{objective}</objective>"
                    for objective in module.learning_objectives
                )
                + "\n\t\t</learning_objectives>\n"
                f"\t\t</module>"
                for module in self.modules
            )
            + "\n\t</modules>\n"
            + "</curriculum>"
        )
