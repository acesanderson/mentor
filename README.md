# Mentor Project

## Project Purpose

Mentor is an AI-powered curriculum generation system that creates curated learning paths from video courses. It uses a multi-agent approach with three distinct personas (L&D specialist, curriculum structuring specialist, and course librarian) to analyze topics, design structured curricula, and select relevant courses from a course database through retrieval-augmented generation (RAG). The system evaluates curriculum quality through similarity scoring, learner progression analysis, and sequence recommendations.

## Architecture Overview

- **mentor.mentor.mentor**: Core curriculum generation pipeline orchestrating three AI personas to produce course curations from topic descriptions
- **mentor.agentic.mentor_agent**: ReACT-based agent that uses tools (similarity search, L&D review, learner feedback) to iteratively build curations
- **mentor.agentic.mentor_chat**: Interactive CLI chat interface for building and managing curations with commands for course research, curation editing, and LLM-powered consultation
- **mentor.evaluation.evaluation**: Evaluation functions for curriculum review, learner progression simulation, audience classification, and title generation
- **mentor.evaluation.sequence**: Sequence recommendation engine that determines optimal course ordering within curations
- **mentor.evaluation.score_curation**: Embedding-based similarity scoring system comparing generated curations against existing certificates
- **mentor.mentor.CurriculumModule**: Pydantic data models defining structured curriculum and module representations
- **mentor.evaluation.levenshtein**: Levenshtein distance-based curriculum comparison for finding similar existing curations

## Dependencies

- **conduit**: LLM orchestration framework providing prompts, models, parsers, and caching
- **Curator/curator**: Course similarity search and retrieval system
- **Kramer/kramer**: Course data management including Course, Curation, and database access
- **pydantic**: Data validation and structured output parsing
- **sentence-transformers**: Embedding generation for curriculum similarity scoring
- **rich**: Terminal UI formatting and markdown rendering
- **Levenshtein**: String distance calculations

Note: `Curator`, `Kramer`, and `conduit` appear to be local/internal dependencies within the ecosystem.

## API Documentation

### Main Entry Points

**Mentor(topic: str, cache: bool = True, return_curriculum: bool = False) -> Curation | tuple[Curriculum, Curation]**

Primary function that generates a complete curriculum curation for a given topic. Executes the full three-stage pipeline (L&D design, curriculum structuring, course selection). Returns a Curation object with selected courses, or optionally both the Curriculum and Curation objects.

Parameters:
- `topic`: Subject matter for the curriculum
- `cache`: Whether to use cached LLM responses
- `return_curriculum`: If True, returns both Curriculum and Curation objects

### Evaluation Functions

**review_curriculum(curation: Curation, audience: str, model=Model("claude")) -> str**

Generates an L&D expert critique of a curriculum for a specified audience.

**learner_progression(curation: Curation, audience: str, model=Model("llama3.1:latest")) -> str**

Simulates a learner's experience going through courses sequentially, providing feedback from the target audience perspective.

**classify_audience(curation: Curation | Course | str, model=Model("llama3.1:latest")) -> str**

Classifies the intended audience for curriculum content.

**recommend_sequence(curation: Curation, preferred_model="claude") -> Sequence**

Analyzes course content and recommends optimal sequencing with rationale.

**title_certificate(curation: Curation, model=Model("llama3.1:latest")) -> str**

Generates suggested titles for a curriculum based on content analysis.

### Data Models

**Curriculum**

Structured representation of a curriculum with topic, description, audience, and modules.

**Module**

Individual curriculum module with title, description, and learning objectives.

**Curation**

Collection of courses with metadata, providing access to combined transcripts, TOCs, and descriptions via `.snapshot`, `.TOCs`, `.transcript` properties.

**Sequence**

Recommended course ordering with `recommended_sequence` (list of tuples) and `rationale` fields.

### Interactive Chat

**MentorChat(model: Model)**

Chat interface extending `conduit.chat.Chat` with commands for curation building:
- Course research: `/curate`, `/mentor`, `/lens`, `/grep`
- Curation editing: `/add course`, `/remove course`, `/move up/down`
- Viewing: `/view curation`, `/view snapshot`, `/view duration`
- Consultation: `/consult lnd`, `/consult learner`, `/consult sequence`

## Usage Examples

### Basic Curriculum Generation

```python
from mentor import Mentor

# Generate a complete curriculum for a topic
curation = Mentor("Python for Data Analysis")

# Access the selected courses
for course in curation.courses:
    print(course.course_title)

# Get curriculum structure along with curation
curriculum, curation = Mentor(
    "Cloud Security Fundamentals", 
    return_curriculum=True
)

# Examine curriculum modules
for module in curriculum.modules:
    print(f"{module.title}: {module.description}")
```

### Curriculum Evaluation

```python
from mentor import Mentor, review_curriculum, learner_progression, recommend_sequence

# Generate and evaluate a curriculum
curation = Mentor("Machine Learning Engineering")

# Get expert review
review = review_curriculum(curation, audience="Software Engineers")
print(review)

# Simulate learner experience
feedback = learner_progression(curation, audience="Data Scientists")
print(feedback)

# Get recommended sequence
sequence = recommend_sequence(curation)
for order, course_title in sequence.recommended_sequence:
    print(f"{order}. {course_title}")
print(f"Rationale: {sequence.rationale}")
```

### Interactive Curation Building

```python
from mentor.agentic.mentor_chat import MentorChat
from conduit import Model

# Start interactive chat session
model = Model("claude")
chat = MentorChat(model)
chat.chat()

# Within chat, use commands:
# /mentor Python for Business Analysts
# /add course 1 3 5
# /consult sequence
# /view curation
# /save pro
```