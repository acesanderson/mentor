# Mentor: Learning Path Generation

## Overview

Welcome to the **Mentor: Learning Path Generation** project! This project is designed to facilitate the creation of tailored learning paths using advanced AI-driven models. Whether you're involved in corporate training or personal career development, this tool helps you design effective, structured curricula from a vast library of video courses.

## Key Features

- **AI-Powered Curation**: Uses language models to design and structure comprehensive learning paths.
- **Custom Learning Paths**: Generates curricula based on specified topics, complete with organized modules and objectives.
- **Video Course Integration**: Selects appropriate video courses aligned with outlined learning objectives.
- **Structured Output**: Provides well-organized JSON representations of curricula for easy integration into Learning Management Systems (LMS).

## How It Works

1. **Define a Topic**: Start by specifying the topic of interest for the learning path.
2. **Generate Curriculum**: An experienced L&D model provides an ideal curriculum outline.
3. **Structure Curriculum**: A Curriculum Structuring Specialist model converts the outline into a machine-readable format.
4. **Course Curation**: Video Course Librarian model selects the best-fitting courses to match the curriculum objectives.

## Caveats
- LLM models are non-deterministic, and you will get different results on each run of the script.
- The RAG pipeline (from [Curator](https://github.com/acesanderson/Curator)) does its best to find the most relevant courses, but will struggle if there isn't a clear match. 

## Dependencies
- See requirements.txt for pip packages

## User Guide

### Prerequisites

- Python 3.x
- Install required Python packages using: 
  ```bash
  pip install -r requirements.txt
  ```
- You need to install the following additional packages:
 - [Curator](https://github.com/acesanderson/Curator): for the Librarian to be able to access course data
 - [Chain](https://github.com/acesanderson/Chain): for our LLM calls

### Running the Program

1. **Clone the Repository**: Download the project files.
   ```bash
   git clone <repository-url>
   cd Mentor-Learning-Path-Generation
   ```

2. **Access Command-Line**: Navigate to the project directory.

3. **Execute Script**: Run the Mentor program with a specified topic.
   ```bash
   python Mentor.py "<Your-Topic-Here>"
   ```
   Replace `<Your-Topic-Here>` with your desired topic, e.g., "Data Science Basics".

4. **View Results**: The console will display:
   - An ideal curriculum plan for the topic.
   - A JSON representation of the structured curriculum.
   - A selection of suitable video courses (Curation object).

### Example

For generating a learning path on "Data Science Basics":
```bash
python Mentor.py "Data Science Basics"

{
  "topic": "Data Science Basics",
  "course_titles": [
    "Introduction to Data Science",
    "Probability Foundations for Data Science",
    "pandas Essential Training",
    "Data Visualization with Matplotlib and Seaborn",
    "Artificial Intelligence Foundations: Machine Learning",
    "Intermediate SQL for Data Scientists",
    "Foundations of Responsible AI",
    "Ethics and Law in Data Analytics"
  ]
}
```

### Upcoming Features
- LP copy generation for resulting Curation object
- Agentic workflows that send reviews back to Librarian




