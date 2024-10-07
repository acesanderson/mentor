# Mentor: Learning Path Generation

## Overview

Welcome to the **Mentor: Learning Path Generation** project! This project is designed to facilitate the creation of tailored learning paths using advanced AI-driven models. Whether you're involved in corporate training or personal career development, this tool helps you design effective, structured curricula from a vast library of video courses.

## Key Features

- **AI-Powered Curation**: Uses language models to design and structure comprehensive learning paths.
- **Custom Learning Paths**: Generates curricula based on specified topics, complete with organized modules and objectives.
- **Video Course Integration**: Selects appropriate video courses aligned with outlined learning objectives.
- **Structured Output**: Provides well-organized JSON representations of curricula for easy integration into Learning Management Systems (LMS).

## Target Audience

This tool is ideal for:

- **Learning & Development Professionals**: Seeking to create effective training programs for employees.
- **Curriculum Designers**: Looking to structure detailed curricula in a digital format.
- **Educational Technologists**: Who require a seamless way to integrate learning paths into existing systems.
- **Corporate Trainers**: Who need resources for employee skill enhancement and career development.

## How It Works

1. **Define a Topic**: Start by specifying the topic of interest for the learning path.
2. **Generate Curriculum**: An experienced L&D model provides an ideal curriculum outline.
3. **Structure Curriculum**: A Curriculum Structuring Specialist model converts the outline into a machine-readable format.
4. **Course Curation**: Video Course Librarian model selects the best-fitting courses to match the curriculum objectives.

## User Guide

### Prerequisites

- Python 3.x
- Install required Python packages using: 
  ```bash
  pip install -r requirements.txt
  ```
- Basic understanding of command-line usage.

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
```

## Support and Contributions

For support or to contribute to this project:

- **Issues**: Find a bug or have a feature request? Raise an issue in the project's GitHub repository.
- **Contributions**: We welcome improvements, bug fixes, and feature suggestions!

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

---

Thank you for using Mentor: Learning Path Generation! We hope this tool enhances your educational initiatives and empowers your learning strategies.
