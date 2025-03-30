"""
1. Programming Generative AI: From Variational Autoencoders to Stable Diffusion with PyTorch and Hugging Face
>> /consult prereqs 1
Model: o3-mini   Query: [Message(role='system', content='You are an expert curriculu...
Cache hit!
---------------------------------------------------------------------
Programming Generative AI: From Variational Autoencoders to Stable Diffusion with PyTorch and Hugging Face
---------------------------------------------------------------------
• Proficient Python programming skills
• Fundamental understanding of deep learning concepts (e.g., neural networks, gradient descent, and backpropagation)
• Basic knowledge of linear algebra and tensor/matrix operations
• Familiarity with interactive coding environments (e.g., Jupyter Notebook or Google Colab)

Rough draft of a chatbot for building curations.
TODO:
- [ ] implement lazy loading
- [ ] suppress logging from Curator
- [ ] get queries to work
- [x] allow multiple params for query commands
- [x] fix encoding issues
- [x] implement numbering for courses, and referencing by number
- [x] implement a workspace for courses
- [x] query_model middleware parsing templates
"""

from rich.console import Console

# our imports
# -----------------------------------------------------------------
console = Console(width=120)  # for spinner

with console.status("[green]Loading...", spinner="dots"):
    from Chain import Chat, Model, Prompt, Chain, Message, MessageStore
    from Kramer import (
        Course,
        Curation,
    )
    import readline  # This silently enables input history for `input`
    from rich.markdown import Markdown
    from datetime import timedelta
    import json
    from typing import TypeVar, Generic
    from enum import Enum
    from pathlib import Path
    import re

# Configs
dir_path = Path(__file__).parent
curation_save_file = dir_path / ".curation.json"
log_file = dir_path / ".chat_log.txt"
Chain._message_store = MessageStore(log_file=log_file)
_ = readline.get_current_history_length()
T = TypeVar("T")  # This is part of the dance to make UniqueList work as a type hint.
system_prompt_file = dir_path / "system_prompt.jinja"


class UniqueList(list, Generic[T]):  # Note the use of our TypeVar T here.
    """
    Our own data structure for a list that only allows unique elements.
    Our various course inventories (including Curation.courses) will be stored in this.
    """

    def append(self, item):
        if item not in self:
            super().append(item)


class MoveDirection(Enum):
    UP = "up"
    DOWN = "down"
    TOP = "top"
    BOTTOM = "bottom"


class MentorChat(Chat):
    def __init__(self, model):
        super().__init__(model)
        self.welcome_message = "[green]Hello! Let's build a Curation together.[/green]"
        # Our simple system prompt
        self.system_prompt = system_prompt_file.read_text()
        # The console for printing
        self.console = console
        # The Curation we're building in the chat
        self.curation: Curation = self.load_curation()
        # Workspace = a bucket for all courses that have come up in the chat, either from user input, curate, mentor, etc.
        self.workspace: UniqueList[Course] = UniqueList()
        # A blacklist
        self.blacklist: UniqueList[Course] = UniqueList()
        # A course cache (for short term memory of numbers-> courses)
        self.course_cache: dict[int, str] = {}
        # We want a log file for this one.
        self.log_file = log_file
        # Save curriculum if it's generated.
        self.curriculum = None
        # Last cert you viewed -- saved in case you want to look at it again or promote it to curation
        self.last_cert = None

    # Functions
    def query_model(self, input: list[Message]) -> str | None:
        """
        Middleware that intercepts the query to parse user templates.
        User templates:
        {{snapshot}} = curation snapshot (i.e. descriptions)
        {{tocs}} = curation tocs
        {{course.transcript}} = a course (retrieved with parse_course_request)
        {{course.description}} = description of a course (retrieved with parse_course_request)
        {{course.toc}} = toc of a course (retrieved with parse_course_request)
        """
        # Load the original function
        _query_model = super().query_model
        # Extract the prompt string from input
        new_prompt = str(input[-1].content)
        # Parse user queries. First, the easy substitutions.
        if "{{snapshot}}" in new_prompt:
            new_prompt = new_prompt.replace(
                "{{snapshot}}",
                f"<course_descriptions>\n{self.curation.snapshot}\n</course_descriptions>",
            )
        if "{{tocs}}" in new_prompt:
            new_prompt = new_prompt.replace(
                "{{tocs}}",
                f"<course_tocs>\n{self.curation.TOCs}\n</course_tocs>",
            )
        # Now for course-specific substitutions.
        VALID_KEYWORDS = ["transcript", "description", "toc"]
        pattern = r"{{(.*?)\.(.*?)}}"
        matches = re.findall(pattern, new_prompt)
        for match in matches:
            # Parse the compound command
            course_param, keyword = match
            if keyword not in VALID_KEYWORDS:
                continue
            course = self.parse_course_request(course_param)
            if not isinstance(course, Course):
                self.console.print("Not found. Did you mean:", style="red")
                self.print_course_list(course)
                return
            # Build the content string
            template_string_to_be_replaced = "{{" + course_param + "." + keyword + "}}"
            replacement_content = None
            if keyword == "transcript":
                replacement_content = course.course_transcript
            elif keyword == "description":
                replacement_content = course.metadata["Course Description"]
            elif keyword == "toc":
                replacement_content = course.course_TOC
            if replacement_content:
                new_prompt = new_prompt.replace(
                    template_string_to_be_replaced,
                    f"<course>\n<course_title>\n{course.course_title}\n</course_title>\n<course_{keyword}>\n{replacement_content}\n</course_{keyword}>\n</course>",
                )
        # Replace the prompt in the input
        input[-1].content = new_prompt
        return _query_model(input)

    def parse_course_request(self, course_request) -> Course | list[Course] | None:
        """
        Parse a course request string.
        If the course request is a number less than 100, return the course at that index in the workspace or the curation.
        Numbering: starts in curation, then workspace.
        If course request is a string, return the course with that ID. (Get already parses course IDs v. titles)
        """
        from Kramer import Get

        if (
            " " in course_request and course_request.replace(" ", "").isdigit()
        ):  # Multiple numbers
            course_numbers = [int(x) for x in course_request.split(" ")]
            course_list = []
            for course_number in course_numbers:
                try:
                    course_title = self.course_cache[course_number]
                    course = Get(course_title)
                    course_list.append(course)
                except KeyError:
                    self.console.print("[red]Invalid course number.[/red]")
                    return None
            return course_list
        if course_request.isdigit():  # Single number, either an index or a course ID
            course_number = int(course_request)
            if course_number < 100:
                try:
                    course_title = self.course_cache[course_number]
                    return Get(course_title)
                except KeyError:
                    self.console.print("[red]Invalid course number.[/red]")
                    return None
            else:
                return Get(course_request)
        else:
            return Get(course_request, return_recommendations=True)

    def add_to_workspace(self, payload: Course | list[Course] | str | list[str]):
        """
        Add a course or courses to workspace, if not already there.
        """
        from Kramer import Get

        course_titles = [course.course_title for course in self.workspace]
        if isinstance(payload, Course):
            if payload.course_title not in course_titles:
                self.workspace.append(payload)
        elif isinstance(payload, list):
            for item in payload:
                self.add_to_workspace(item)
        elif isinstance(payload, str):
            course = Get(payload)
            if course:
                if course.course_title not in course_titles:
                    self.workspace.append(course)
            else:
                raise ValueError(
                    f"Course not found: this suggests an error in code. Input = {payload}"
                )

    def convert_duration(self, duration: str | int) -> str:
        """
        Convert a duration in seconds to a 00:00:00 format.
        """
        if isinstance(duration, str):
            duration = int(duration)
        time_str = str(timedelta(seconds=duration))
        return time_str

    def save_curation(self):
        with open(curation_save_file, "w") as f:
            json.dump(self.curation.model_dump_json(), f)

    def load_curation(self) -> Curation:
        if curation_save_file.exists():
            with open(curation_save_file, "r") as f:
                try:
                    curation = Curation.model_validate_json(json.load(f))
                    return curation
                except:
                    self.console.print("Error validating curation from file.")
                    return Curation(title="", courses=UniqueList())
        else:
            return Curation(title="", courses=UniqueList())

    def convert_urls(self, urls: str) -> str:
        return urls.split(",")[0]

    def update_course_cache(self, courselist: list[Course]):
        """
        Update the course cache with a new list of courses.
        This is invoked whenever a course list is printed to user (therefore from print_course_list).
        """
        self.course_cache = {}
        for index, course in enumerate(courselist):
            self.course_cache[index + 1] = course.course_title

    def print_course_list(self, courselist: list[Course]):
        """
        Formats courselist (with numbers) and prints to console.
        Invoked whenever we want to present a course list to a user.
        """
        for index, course in enumerate(courselist):
            try:
                course_release_date = course.metadata["Course Release Date"][:4]
            except (KeyError, TypeError):
                course_release_date = ""
            self.console.print(
                f"[green]{index+1}[/green]. [yellow]{course.course_title:<80}[/yellow][cyan]{course_release_date}[/cyan]"
            )
        self.update_course_cache(courselist)

    def number_courses(self) -> dict:
        """
        Number the courses in the curation and workspace.
        Returns a dictionary with keys "curation" and "workspace", each with a list of tuples (number, course, whole catalog).
        "curation" and "workspace" are for rendering the curation and workspace views.
        Catalog is for retrieving courses by number.
        """
        if self.curation:
            curation_courses = self.curation.courses
        else:
            curation_courses = UniqueList()
        workspace_courses = self.workspace  # First, number the courses in the curation
        numbered_curation = [
            (i + 1, course) for i, course in enumerate(curation_courses)
        ]
        # Then, number the courses in the workspace
        last_number = numbered_curation[-1][0] if numbered_curation else 0
        numbered_workspace = [
            (i + last_number + 1, course) for i, course in enumerate(workspace_courses)
        ]
        # Create a catalog of all courses
        catalog = {x[0]: x[1] for x in numbered_curation + numbered_workspace}
        return {
            "curation": numbered_curation,
            "workspace": numbered_workspace,
            "catalog": catalog,
        }

    def move_course(self, course: Course, direction: MoveDirection):
        """
        Move a course in the curation.
        """
        if course in self.curation.courses:
            index = self.curation.courses.index(course)
            if direction == MoveDirection.UP:
                if index > 0:
                    self.curation.courses[index], self.curation.courses[index - 1] = (
                        self.curation.courses[index - 1],
                        self.curation.courses[index],
                    )
                    # Print the new curation for user
                    self.print_course_list(self.curation.courses)
                    # Refresh the course_cache
                    self.update_course_cache(self.curation.courses)
                    # Save the curation
                    self.save_curation()
                else:
                    self.console.print("[red]Already at top.[/red]")
            elif direction == MoveDirection.DOWN:
                if index < len(self.curation.courses) - 1:
                    self.curation.courses[index], self.curation.courses[index + 1] = (
                        self.curation.courses[index + 1],
                        self.curation.courses[index],
                    )
                    # Print the new curation for user
                    self.print_course_list(self.curation.courses)
                    # Refresh the course_cache
                    self.update_course_cache(self.curation.courses)
                    # Save the curation
                    self.save_curation()
                else:
                    self.console.print("[red]Already at bottom.[/red]")
            elif direction == MoveDirection.TOP and index > 0:
                self.curation.courses.insert(0, self.curation.courses.pop(index))
                # Print the new curation for user
                self.print_course_list(self.curation.courses)
                # Refresh the course_cache
                self.update_course_cache(self.curation.courses)
                # Save the curation
                self.save_curation()
            elif (
                direction == MoveDirection.BOTTOM
                and index < len(self.curation.courses) - 1
            ):
                # Print the new curation for user
                self.print_course_list(self.curation.courses)
                # Refresh the course_cache
                self.update_course_cache(self.curation.courses)
                self.curation.courses.append(self.curation.courses.pop(index))
                # Save the curation
                self.save_curation()
        else:
            print("[red]Course not in curation.[/red]")

    # Commands
    ## Our research functions
    def command_get_description(self, param):
        """
        Get the description of a course.
        """
        course = self.parse_course_request(param)
        if course:
            if isinstance(course, Course):
                self.console.print(course.metadata["Course Description"])
                self.add_to_workspace(course)
            elif isinstance(course, list):
                self.console.print("Not found. Did you mean:", style="red")
                self.print_course_list(course)

    def command_get_data(self, param):
        """
        Get a useful subset of metadata of a course.
        """
        course = self.parse_course_request(param)
        if course:
            if isinstance(course, Course):
                metadata = {
                    k: course.metadata[k]
                    for k in [
                        "Course ID",
                        "Course Name",
                        "Course Description",
                        "LIL URL",
                        "Instructor Name",
                        "Instructor Short Bio",
                        "Course Release Date",
                        "Visible Duration",
                        "Internal Library",
                        "Internal Subject",
                        "LI Level",
                    ]
                }
                # Convert duration to a human-readable format
                metadata["Visible Duration"] = self.convert_duration(
                    metadata["Visible Duration"]
                )
                # Grab just first URL
                metadata["LIL URL"] = self.convert_urls(metadata["LIL URL"])
                # Scrunch title + id
                metadata["Course Name"] = (
                    f"{metadata['Course Name']} - {metadata['Course ID']}"
                )
                metadata.pop("Course ID")
                # Scrunch instructor + bio
                metadata["Instructor Name"] = (
                    f"{metadata['Instructor Name']} - {metadata['Instructor Short Bio']}"
                )
                metadata.pop("Instructor Short Bio")
                # Scrunch library + subject
                metadata["Internal Library"] = (
                    f"{metadata['Internal Library']} - {metadata['Internal Subject']}"
                )
                metadata.pop("Internal Subject")
                metadata["LI Level"] = f"{metadata['LI Level']}"
                formatted = [
                    f"[green]{k}[/green]: [yellow]{v}[/yellow]"
                    for k, v in metadata.items()
                ]
                self.console.print("\n".join(formatted))
                self.add_to_workspace(course)
            elif isinstance(course, list):
                self.console.print("Not found. Did you mean:", style="red")
                self.print_course_list(course)

    def command_get_toc(self, param):
        """
        Get the table of contents of a course.
        """
        course = self.parse_course_request(param)
        if course:
            if isinstance(course, Course):
                self.console.print(course.course_TOC)
                self.add_to_workspace(course)
            elif isinstance(course, list):
                self.console.print("Not found. Did you mean:", style="red")
                self.print_course_list(course)

    def command_get_transcript(self, param):
        """
        Get the transcript of a course.
        """
        course = self.parse_course_request(param)
        if course:
            if isinstance(course, Course):
                self.console.print(course.course_transcript)
                self.add_to_workspace(course)
            elif isinstance(course, list):
                self.console.print("Not found. Did you mean:", style="red")
                self.print_course_list(course)

    def command_get_url(self, param):
        """
        Get the URL of a course.
        """
        course = self.parse_course_request(param)
        if course:
            if isinstance(course, Course):
                self.console.print(course.metadata["Course URL"])
                self.add_to_workspace(course)
            elif isinstance(course, list):
                self.console.print("Not found. Did you mean:", style="red")
                self.print_course_list(course)

    def command_get_tocs(self):
        """
        Get the combined table of contents of the curation.
        """
        if not self.curation:
            self.console.print("[red]No curation.[/red]")
            return
        tocs = self.curation.TOCs
        self.console.print(tocs)

    def command_view_snapshot(self):
        """
        Get the combined descriptions of the curation.
        """
        if not self.curation:
            self.console.print("[red]No curation.[/red]")
            return
        snapshot_text = self.curation.get_snapshot("markdown")
        snapshot_text = Markdown(snapshot_text)
        self.console.print(snapshot_text)

    def command_view_difficulty(self):
        """
        Get the difficulty (LI Level) for each course.
        """
        if len(self.curation.courses) == 0:
            self.console.print("[red]No courses in Curation.[/red]")
            return
        output = ""
        if self.curation.title:
            output += f"[bold cyan]{self.curation.title}[/bold cyan]\n"
        for index, course in enumerate(self.curation.courses):
            output += f"[green]{index+1}[/green]. [yellow]{course.course_title:<80}[/yellow][cyan]{course.metadata["LI Level"]}[/cyan]\n"
        self.console.print(output)

    def command_view_feedback(self):
        """
        Get learner feedback for a course.
        """
        from Kramer import get_feedback_by_course_id

        if len(self.curation.courses) == 0:
            self.console.print("[red]No courses in Curation.[/red]")
            return
        output = ""
        ratings = []
        if self.curation.title:
            output += f"[bold cyan]{self.curation.title}[/bold cyan]\n"
        for index, course in enumerate(self.curation.courses):
            course_id = course.course_admin_id
            feedback = get_feedback_by_course_id(course_id)
            if feedback:
                course_rating = feedback[1]
                no_of_ratings = feedback[2]
                normalized = (
                    2.5 * course_rating - 7.5
                )  # The data is actually 3-5, so we want to normalize it to 0-5
                ratings.append(course_rating)
                output += f"[green]{index+1}[/green]. [yellow]{course.course_title:<80}[/yellow][cyan]{course_rating:.2f}[/cyan] from [green]{no_of_ratings} ratings.[/green] ({normalized:.2f})\n"
            else:
                output += f"[green]{index+1}[/green]. [yellow]{course.course_title:<80}[/yellow][red]No feedback available.[/red]\n"
        # Calculate the overall score of the curation
        if ratings:
            overall_score = sum(ratings) / len(ratings)
            output += f"\n[bold green]Overall score: {overall_score:.2f}[/bold green]\n"
        else:
            output += "[red]No feedback available for any courses.[/red]\n"
        self.console.print(output)

    def command_head(self, param):
        """
        Get the first transcript of a course.
        """
        course = self.parse_course_request(param)
        if course:
            if isinstance(course, Course):
                head = course.head
                if head:
                    self.console.print(head)
                else:
                    self.console.print("[red]No head found.[/red]")
                self.add_to_workspace(course)
            elif isinstance(course, list):
                self.console.print("Not found. Did you mean:", style="red")
                self.print_course_list(course)

    def command_tail(self, param):
        """
        Get the last transcript of a course.
        """
        course = self.parse_course_request(param)
        if course:
            if isinstance(course, Course):
                tail = course.tail
                if tail:
                    self.console.print(tail)
                else:
                    self.console.print("[red]No tail found.[/red]")
                self.add_to_workspace(course)
            elif isinstance(course, list):
                self.console.print("Not found. Did you mean:", style="red")
                self.print_course_list(course)

    def command_instructor(self, param):
        """
        Get a list of courses by instructor name.
        """
        from Kramer import instructor_courses

        instructor = param
        hits = instructor_courses(instructor)
        if hits:
            self.print_course_list(hits)
            self.add_to_workspace(hits)
        else:
            self.console.print("No courses found.", style="red")

    def command_curate(self, param):
        """
        Similarity search courses by a query string.
        Logic is custom since Curator returns course name and score (not Course objects).
        """
        from Curator import Curate
        from Kramer import Get

        query = param
        results = Curate(query, n_results=100, k=10)
        results = [(Get(course), score) for course, score in results]
        if any([course == None for (course, _) in results]):
            self.console.print(
                "[red]Some courses not found; this suggests an error in code.[/red]"
            )
            return
        if results:
            for index, result in enumerate(results):
                course = result[0]
                score = result[1]
                course_title = course.course_title
                try:
                    course_release_date = course.metadata["Course Release Date"][:4]
                except (KeyError, TypeError):
                    course_release_date = ""
                self.console.print(
                    f"[green]{index+1}[/green]. [yellow]{course_title: <80}[/yellow]\t[magenta]{score}[/magenta]\t[cyan]{course_release_date}[/cyan]"
                )
        self.course_cache = {
            index + 1: course.course_title for index, (course, _) in enumerate(results)
        }
        self.add_to_workspace([course for (course, _) in results])

    def command_mentor(self, param):
        """
        Have a Mentor generate a Curation.
        """
        from Mentor import Mentor

        query = param
        curriculum, mentor_curation = Mentor(query, return_curriculum=True)
        self.curriculum = curriculum  # type: ignore
        if mentor_curation:
            self.print_course_list(mentor_curation.courses)  # type: ignore
            self.add_to_workspace(mentor_curation.courses)  # type: ignore
        else:
            raise ValueError("Mentor returned None.")

    ## Get certs!
    def command_get_cert(self, param):
        """
        Get a cert for comparison purposes.
        """
        from Kramer.certs.GetCert import GetCert

        if param == "last":
            cert = self.last_cert
        else:
            cert_title = param
            cert = GetCert(cert_title, print_suggestions=False)
        # If not a complete match, just print out the top fuzzy match.
        if isinstance(cert, list):
            cert = cert[0]
        self.console.print(f"[bold green]{cert.title}[/bold green]")  # type: ignore
        self.print_course_list(cert.courses)  # type: ignore
        self.last_cert = cert
        self.add_to_workspace(cert.courses)  # type: ignore

    def command_add_cert(self):
        """
        This takes the last cert viewed (through /get cert) and makes it the active curation.
        """
        self.curation = self.last_cert
        self.save_curation()
        self.console.print("[green]Curation replaced with last cert viewed.[/green]")

    ## Our functions for building / editing curations
    def command_name_curation(self, param):
        """
        Assign a name to the curation. Necessary for saving, creating learning paths, and using many of the consult commands.
        """
        name = param
        self.curation.title = name
        self.save_curation()
        self.console.print(f"[green]Curation title changed: {name}[/green]")

    def command_view_duration(self):
        """
        View the duration of the current curation.
        """
        if not self.curation.courses:
            self.console.print("[red]No courses in Curation.[/red]")
            return
        duration = self.curation.duration
        self.console.print(duration)

    def command_view_curation(self):
        """
        View the current curation, with numbers.
        """
        if self.curation == None or self.curation.courses == UniqueList():
            if self.curation.title:
                self.console.print(
                    f"[bold cyan]{self.curation.title}[/bold cyan]\n[red]No courses (yet).[/red]"
                )
            self.console.print("[red]No curation (yet).[/red]")
        else:
            self.console.print(f"[bold cyan]{self.curation.title}[/bold cyan]")
            self.print_course_list(self.curation.courses)

    def command_view_cache(self):
        """
        View the course cache.
        """
        from Kramer import Get

        indices = sorted(list(self.course_cache.keys()))
        courses = []
        for index in indices:
            courses.append(Get(self.course_cache[index]))
        self.print_course_list(courses)

    def command_view_curriculum(self):
        """
        View a curriculum if created.
        """
        from Mentor import Curriculum

        if self.curriculum:
            for module in self.curriculum.modules:
                border = "-" * 120
                self.console.print(border)
                self.console.print(f"[green]{module.title}[/green]")
                self.console.print(border)
                self.console.print(f"[yellow]{module.description}[/yellow]")
                self.console.print(
                    f"[cyan]\t{"\n\t".join(module.learning_objectives)}[/cyan]"
                )
        else:
            self.console.print("[red]No curriculum created.[/red]")
            return

    def command_add_course(self, param):
        """
        Add a course to the curation.
        Allows multiple courses to be added at once.
        """
        course = self.parse_course_request(param)
        if isinstance(course, list):
            if param.replace(
                " ", ""
            ).isdigit():  # If it's a list and the param reduces to digits, it was a bulk request
                for item in course:
                    self.curation.courses.append(item)
                    self.add_to_workspace(item)
                self.save_curation()
            else:  # Otherwise, param didn't find a match and this is a list of recommendations
                self.print_course_list(course)
        elif isinstance(course, Course):
            self.curation.courses.append(course)
            self.add_to_workspace(course)
            self.save_curation()

    def command_remove_course(self, param):
        """
        Remove a course from the curation.
        Allows multiple courses to be removed at once.
        """
        course = self.parse_course_request(param)
        if isinstance(course, list):
            if param.replace(
                " ", ""
            ).isdigit():  # If it's a list and the param reduces to digits, it was a bulk request
                for item in course:
                    self.curation.courses.remove(item)
                    self.add_to_workspace(item)
                self.save_curation()
            else:  # Otherwise, param didn't find a match and this is a list of recommendations
                self.print_course_list(course)
        elif isinstance(course, Course):
            self.curation.courses.remove(course)
            self.add_to_workspace(course)
            self.save_curation()

    def command_clear(self):
        """
        Clear the current curation.
        """
        self.curation = Curation(title="", courses=UniqueList())
        self.console.print("Curation cleared.")
        with open(curation_save_file, "w") as f:
            pass

    # Reorder / move courses around.
    def command_reorder_curation(self):
        """
        Allow user to change the order of courses in the Curation.
        """
        if self.curation == None or self.curation.courses == UniqueList():
            self.console.print("[red]No courses in Curation.[/red]")
            return
        self.print_course_list(self.curation.courses)
        for index, course in enumerate(self.curation.courses):
            self.course_cache[index + 1] = course
        self.console.print(
            "Write the two numbers you want to swap, separated by a space."
        )
        user_input = self.console.input("[bold green]Swap[/bold green]: ")
        swap = user_input.split(" ")
        if len(swap) != 2:
            self.console.print("[red]Invalid input.[/red]")
            return
        try:
            swap = [int(x) for x in swap]
            course1 = self.course_cache[swap[0]]
            course2 = self.course_cache[swap[1]]
            # Swap the courses in self.curation.courses
            index1 = self.curation.courses.index(course1)
            index2 = self.curation.courses.index(course2)
            self.curation.courses[index1] = course2
            self.curation.courses[index2] = course1
            self.course_cache[swap[0]] = course2
            self.course_cache[swap[1]] = course1
            # Print the new curation for user
            self.print_course_list(self.curation.courses)
            # Refresh the course_cache
            self.update_course_cache(self.curation.courses)
            # Save the curation
            self.save_curation()
        except KeyError:
            self.console.print("[red]Invalid course number.[/red]")
        except ValueError:
            self.console.print("[red]Invalid input.[/red]")
        except:
            self.console.print("[red]Invalid input.[/red]")

    def command_move_up(self, param):
        """
        Move a course up in the curation.
        """
        course = self.parse_course_request(param)
        if isinstance(course, Course):
            self.move_course(course, MoveDirection.UP)

    def command_move_down(self, param):
        """
        Move a course down in the curation.
        """
        course = self.parse_course_request(param)
        if isinstance(course, Course):
            self.move_course(course, MoveDirection.DOWN)

    def command_move_bottom(self, param):
        """
        Move a course to the bottom of the curation."
        """
        course = self.parse_course_request(param)
        if isinstance(course, Course):
            self.move_course(course, MoveDirection.BOTTOM)

    def command_move_top(self, param):
        """
        Move a course to the top of the curation.
        """
        course = self.parse_course_request(param)
        if isinstance(course, Course):
            self.move_course(course, MoveDirection.TOP)

    # Save / load functions
    def command_save_curation(self, param):
        """
        Save the current curation to a file.
        """
        filename = param + ".json"
        if self.curation.courses == UniqueList():
            self.console.print("No curation to save.")
        else:
            with open(filename + ".json", "w") as f:
                json.dump(self.curation.model_dump_json(), f)
            self.console.print(f"Curation saved to {filename}.")

    def command_build_learningpath(self):
        """
        Build a Learning Path from the current curation.
        """
        from Kramer import LearningPath, build_LearningPath_from_Curation

        if self.curation.title == "":
            self.console.print(
                f"[red]Curation has no title. Set one with /name curation[/red]"
            )
            return
        elif self.curation.courses == UniqueList():
            self.console.print(
                f"[red]Curation has no courses. Add some with /add course[/red]"
            )
            return
        else:
            if len(self.curation.courses) > 0:
                learning_path: LearningPath = build_LearningPath_from_Curation(
                    self.curation
                )
                learning_path.print_markdown()
                learning_path.save_to_google_doc()
        self.console.print(f"LP saved to {self.curation.title}.md.", style="green")

    ## LLMs! Our special prompt functions
    def command_query_curation(self, param):
        """
        Ask a question about the curation. This uses the snapshot.
        """
        if not self.curation:
            self.console.print("No curation.")
            return
        query = f"Look at this description of a curriculum for an online learning program and then answer the question:\n<curriculum>{self.curation.snapshot}</curriculum>"
        query += f"\n\n<question>{param}</question>"
        prompt = Prompt(query)
        chain = Chain(model=self.model, prompt=prompt)
        response = chain.run()
        self.console.print(response)

    def command_query_TOCs(self, param):
        """
        Ask a question about the combined TOCs of the curation. This uses the TOCs.
        """
        if not self.curation:
            self.console.print("No curation.")
            return
        query = f"Look at this description of a curriculum for an online learning program and then answer the question:\n<curriculum>{self.curation.TOCs}</curriculum>"
        query += f"\n\n<question>{param}</question>"
        prompt = Prompt(query)
        chain = Chain(model=self.model, prompt=prompt)
        response = chain.run()
        self.console.print(response)

    def command_query_transcript(self, param):
        """
        Use a local model to query the transcript of a course. This uses llama3.1:latest for data privacy.
        TODO: This actually requires two parameters: the course ID and the question.
        """
        course = self.parse_course_request(param)
        if course:
            query = f"Look at this transcript of a course and then answer the question:\n<transcript>{course.course_transcript}</transcript>"
            query += f"\n\n<question>{param}</question>"
            prompt = Prompt(query)
            model = Model("llama3.1:latest")
            chain = Chain(model=model, prompt=prompt)
            response = chain.run()
            self.console.print(response)

    def command_lens(self, param):
        """
        "Lens" performs text search across all transcript, returns course titles that contain the query string.
        """
        from Kramer import Lens

        query = param
        hits = Lens(query)
        self.print_course_list(hits)
        self.add_to_workspace(hits)

    def command_laser(self, param):
        """
        "Laser" searches for a query string in all course titles.
        """
        from Kramer import Laser

        query = param
        hits = Laser(query)
        self.print_course_list(hits)
        self.add_to_workspace(hits)

    def command_consult_lnd(self, param):
        """
        Have an L&D expert critique the curation. Need to pass an audience param.
        """
        from Mentor import review_curriculum

        audience = param
        if not self.curation:
            self.console.print("No curation.")
            return
        review = review_curriculum(
            curation=self.curation, audience=audience, model=self.model
        )
        self.console.print(review)

    def command_consult_learner(self, param):
        """
        Have a learner provide feedback on the curation. Need to pass an audience param.
        """
        from Mentor import learner_progression

        audience = param
        if not self.curation:
            self.console.print("No curation.")
            return
        feedback = learner_progression(
            curation=self.curation, audience=audience, model=self.model
        )
        self.console.print(feedback)

    def command_consult_audience(self):
        """
        Classify the audience for the curation.
        """
        from Mentor import classify_audience

        if not self.curation:
            self.console.print("No curation.")
            return
        audience = classify_audience(curation=self.curation, model=self.model)
        self.console.print(audience)

    def command_consult_prereqs(self, param):
        """
        Get prerequisites for a course. (or entire curation -- input "curation")
        """
        from Kramer import get_course_prerequisites, get_curation_prerequisites

        # If user inputs "curation", get prerequisites for all courses in the curation.
        if param == "curation":
            prereqs_dicts: list[dict] = get_curation_prerequisites(self.curation)
            output = ""
            for prereq_dict in prereqs_dicts:
                output = ""
                output += "---------------------------------------------------------------------\n"
                output += f'[green]{prereq_dict["course_title"]}[/green]\n'
                output += "---------------------------------------------------------------------\n"
                output += f'[yellow]{prereq_dict["prerequisites"]}[/yellow]\n'
                self.console.print(output)
        # Or if we have a param, do a single course
        course = self.parse_course_request(param)
        if isinstance(course, Course):
            prerequisites = get_course_prerequisites(course)
            output = ""
            output += "---------------------------------------------------------------------\n"
            output += f"[green]{course.course_title}[/green]\n"
            output += "---------------------------------------------------------------------\n"
            output += f"[yellow]{prerequisites}[/yellow]\n"
            self.console.print(output)
        else:
            raise ValueError("Course not found.")

    def command_consult_first_course(self, param):
        """
        Consult for a curation based on the first, foundational course.
        """
        from Kramer.courses.FirstCourse import first_course, pretty_curriculum

        course = self.parse_course_request(param)
        try:
            first_course_curriculum = first_course(course.course_title)
        except AttributeError:
            self.console.print("Course not found.")
            return
        self.console.print(Markdown(pretty_curriculum(first_course_curriculum)))

    def command_consult_tools(self, param):
        """
        Go through a course (or curation) to identify orgs and tools mentioned.
        Useful for identifying / crossing out potential partners.
        """
        from Kramer import (
            analyze_course_for_orgs_and_tools,
            analyze_curation_for_orgs_and_tools,
        )

        # If user inputs "curation", get prerequisites for all courses in the curation.
        if param == "curation":
            if len(self.curation) > 0:
                org_counter, tool_counter = analyze_curation_for_orgs_and_tools(
                    self.curation
                )
                combined_counter = org_counter + tool_counter
                combined_counter = list(combined_counter.items())
                combined_counter = sorted(
                    combined_counter, key=lambda x: x[1], reverse=True
                )
                output = ""
                for item in combined_counter:
                    output += f"[green]{str(item[0])}[/green]: [yellow]{str(item[1])}[/yellow]\n"
                self.console.print(output)
            else:
                raise ValueError("Curation is empty.")
        # Or if we have a param, do a single course
        course = self.parse_course_request(param)
        if isinstance(course, Course):
            org_counter, tool_counter = analyze_course_for_orgs_and_tools(course)
            # Combine org_counter and tool_counter into a combined_counter
            combined_counter = org_counter + tool_counter
            combined_counter = list(combined_counter.items())
            combined_counter = sorted(
                combined_counter, key=lambda x: x[1], reverse=True
            )
            output = ""
            for item in combined_counter:
                output += (
                    f"[green]{str(item[0])}[/green]: [yellow]{str(item[1])}[/yellow]\n"
                )
            self.console.print(output)
        else:
            raise ValueError("Course not found.")

    def command_consult_score(self):
        """
        Uses a three dimensional rubric to evaluate curation quality.
        """
        from Winnow.evaluation.curation_rubric.curation_rubric import (
            evaluate_curation_async,
        )

        course_rubrics, final_score = evaluate_curation_async(
            self.curation, verbose=False
        )
        output = ""
        for course_rubric in course_rubrics:
            output += "\n"
            dimension = course_rubric.dimension
            score = course_rubric.score
            rationale = course_rubric.rationale
            output += f"[green]{dimension}[/green]: [cyan]{score:.2f}[/cyan]\n"
            output += f"[green]Rationale:[/green] {rationale}\n"
        output += f"\n[bold green]Final score:[/bold green] [bold yellow]{final_score:.2f}[/bold yellow]\n"
        self.console.print(output)

    def command_consult_sequence(self):
        """
        For the courses in the Curation, provide a detailed recommendation for course order.
        """
        pass

    def command_situate_course(self, param):
        """
        For a given course, speculate on what certificate it would be in, and for whom.
        Also good for understanding prerequisites
        """
        course = self.parse_course_request(param)
        pass

    def command_suggest_partner(self):
        """
        For the current curation, suggest a partner.
        """
        pass

    ## Our commands for managing the workspace
    def command_view_workspace(self):
        """
        View the workspace.
        """
        self.print_course_list(self.workspace)

    def command_add_workspace(self, param):
        """
        Add a course to the workspace.
        """
        course = self.parse_course_request(param)
        if course:
            self.add_to_workspace(course)
            self.console.print(f"{course.course_title} added to workspace.")

    def command_remove_workspace(self, param):
        """
        Remove a course from the workspace.
        """
        course = self.parse_course_request(param)
        course_title = course.course_title
        if course in self.workspace:
            self.workspace.remove(course)
            self.console.print(f"{course_title} removed from workspace.")
        else:
            self.console.print(f"{course_title} not in workspace")

    def command_clear_workspace(self):
        """
        Clear the workspace.
        """
        self.workspace = UniqueList()
        self.console.print("Workspace cleared.", style="green")


if __name__ == "__main__":
    model = Model("claude")
    chat = MentorChat(model)
    chat.chat()
