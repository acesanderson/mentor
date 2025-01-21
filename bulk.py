from Mentor import Mentor
from pprint import pprint as pp

job_titles = """
Tax Manager
Treasury Analyst
Workforce Development Manager
""".strip().split(
    "\n"
)

curations = []
for index, title in enumerate(job_titles):
    curation = Mentor(title)
    print(f"{index+1:02d}. {title}")
    curations.append((title, curation.course_titles))

pp(curations)
