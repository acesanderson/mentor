from Chain import Chain, Prompt, Model, Parser
from Kramer import Curation
from pydantic import BaseModel, Field
from pathlib import Path

# Constants
dir_path = Path(__file__).parent
sequence_prompt_file = dir_path / "prompts" / "sequence_prompt.jinja"
sequence_prompt = sequence_prompt_file.read_text(encoding="utf-8")


# Pydantic model
class Sequence(BaseModel):
    """
    The recommendations from our curriculum developer on the ideal sequence of courses.
    """

    thinking: str = Field(
        description="Your thinking as you develop your recommendation."
    )
    recommended_sequence: list[tuple[int, str]] = Field(
        description="The recommended sequence of courses, with the number of the course in sequence and the course title."
    )
    rationale: str = Field(description="The rationale behind the recommended sequence.")


# Our chain
def recommend_sequence(curation: Curation, preferred_model="claude") -> Sequence:
    """
    Recommend a sequence of courses based on the provided curation.
    """
    prompt = Prompt(sequence_prompt)
    model = Model(preferred_model)
    parser = Parser(Sequence)  # type: ignore
    chain = Chain(prompt=prompt, model=model, parser=parser)
    response = chain.run(input_variables={"snapshot": curation.snapshot})
    return response.content


if __name__ == "__main__":
    from Kramer import get_sample_curation

    curation = get_sample_curation()
    sequence = recommend_sequence(curation)
    print(sequence)
