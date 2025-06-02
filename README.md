# Mentor

**AI-powered curriculum generation for corporate learning programs**

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Mentor automatically generates structured learning curricula from topic descriptions, curates relevant courses from your video library, and provides comprehensive evaluation tools for corporate training programs.

## Quick Start

```bash
# Install Mentor
pip install .

# Generate a curriculum
from Mentor import Mentor
curriculum = Mentor("Data Science for Business Analysts")
print(curriculum)
```

**Output:**
```
Curation: Data Science Fundamentals for Business Analysis
Courses:
1. Excel for Data Analysis
2. Introduction to Python for Data Science
3. Statistical Analysis Fundamentals
4. Data Visualization with Power BI
5. Business Intelligence Reporting
6. Predictive Analytics for Business
```

## Core Features

### 🤖 **AI Curriculum Generation**
- **Topic-to-Curriculum**: Transform any learning topic into a structured curriculum using multi-agent AI workflow
- **Course Curation**: Automatically select and sequence courses from your video library
- **Smart Evaluation**: Built-in quality assessment and learner progression analysis

### 💬 **Interactive Chat Interface**
- **Natural Language Commands**: Research courses, build curricula, and get expert feedback through chat
- **Template System**: Use `{{course.transcript}}`, `{{snapshot}}`, `{{tocs}}` for dynamic content queries
- **Workspace Management**: Organize and manipulate course collections with numbered references

### 📊 **Evaluation & Analytics**
- **Multi-perspective Review**: Get feedback from L&D specialists and simulated learners
- **Sequence Optimization**: AI-recommended course ordering for optimal learning progression
- **Quality Scoring**: Comprehensive rubric-based assessment of curriculum quality

## Installation

```bash
git clone https://github.com/yourusername/Mentor.git
cd Mentor
pip install -e .
```

## Usage Examples

### Programmatic API

```python
from Mentor import Mentor, review_curriculum, recommend_sequence

# Generate a complete curriculum
curriculum = Mentor("Python for Business Analysts")

# Get expert review
review = review_curriculum(curriculum, audience="Business Analysts")

# Optimize course sequence
sequence = recommend_sequence(curriculum)
```

### Interactive Chat Mode

```python
from Mentor.agentic import MentorChat
from Chain import Model

chat = MentorChat(Model("claude"))
chat.chat()
```

**Chat Commands:**
```bash
/mentor "Machine Learning for Marketing"  # Generate curriculum
/curate "data visualization"              # Search similar courses  
/add course 1 2 3                        # Add courses to curation
/consult sequence                         # Get recommended ordering
/view curation                            # Show current curriculum
```

## Architecture

Mentor uses a three-agent workflow:

1. **L&D Specialist**: Designs ideal curriculum structure from topic description
2. **Curriculum Specialist**: Converts designs into structured learning modules  
3. **Course Librarian**: Maps modules to actual courses using RAG (Retrieval-Augmented Generation)

Each agent has specialized prompts and expertise areas, ensuring high-quality, pedagogically sound curricula.

## Key Components

| Component | Purpose |
|-----------|---------|
| `Mentor()` | Main curriculum generation function |
| `MentorChat` | Interactive curriculum building interface |
| `review_curriculum()` | Expert evaluation of learning paths |
| `recommend_sequence()` | AI-optimized course ordering |
| `Curriculum` | Structured curriculum data model |

## Configuration

Mentor integrates with your existing course library through the `Curator` and `Kramer` modules (course search and retrieval). Configure your course database connection in the respective modules.

## Contributing

Mentor is designed for corporate learning teams building at scale. See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and contribution guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Need help?** Mentor is optimized for corporate training environments with large video course libraries. For support with integration or customization, please open an issue.
