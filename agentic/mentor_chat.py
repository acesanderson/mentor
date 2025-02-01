"""
Rough draft of a chatbot for building curations.
TODO:
- use a simple list for self.curation
- user can "bless" curation into a Curation object, giving it a title.
- user can generate LP from Curation object
"""

from Chain import Chat, Model, Prompt, Chain
from Curator import Curate
from Kramer import Course, Get, Curation, build_LearningPath_from_Curation
from Mentor import (
    Mentor,
    review_curriculum,
    title_certificate,
    classify_audience,
    learner_progression,
)
import readline  # This silently enables input history for `input`
from rich.console import Console
from datetime import timedelta

_ = readline.get_history_item(1)  # Minimal interaction to silence IDE


class MentorChat(Chat):
    def __init__(self, model):
        super().__init__(model)
        self.welcome_message = "[green]Hello! Let's build a Curation together.[/green]"
        self.console = Console(width=120)
        # The Curation we're building in the chat
        self.curation: Curation | None = (
            None  # TODO: Curations require titles, which makes this a bit more complex
        )
        # A sort of scratchpad area for courses I'm considering
        self.workspace: list[Course] = []
        # A blacklist
        self.blacklist: list[Course] = []

    # Functions
    def parse_course_request(self, course_request) -> Course | None:
        """
        Parse a course request string.
        If the course request is a number less than 100, return the course at that index in the workspace or the curation.
        Numbering: starts in curation, then workspace.
        If course request is a string, return the course with that ID. (Get already parses course IDs v. titles)
        """
        if course_request.isdigit():
            course_number = int(course_request)
            if course_number < 100:
                return self.number_courses()["catalog"][course_number]
            else:
                return Get(course_request)
        else:
            return Get(course_request)

    def convert_duration(self, duration: str | int) -> str:
        """
        Convert a duration in seconds to a 00:00:00 format.
        """
        if isinstance(duration, str):
            duration = int(duration)
        time_str = str(timedelta(seconds=duration))
        return time_str

    def convert_urls(self, urls: str) -> str:
        return urls.split(",")[0]

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
            curation_courses = []
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

    # Commands
    ## Our research functions
    def command_get_description(self, param):
        """
        Get the description of a course.
        """
        course = self.parse_course_request(param)
        if course:
            print(course.metadata["Course Description"])

    def command_get_data(self, param):
        """
        Get a useful subset of metadata of a course.
        """
        course = self.parse_course_request(param)
        if course:
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
            formatted = [
                f"[green]{k}[/green]: [yellow]{v}[/yellow]" for k, v in metadata.items()
            ]
            self.console.print("\n".join(formatted))

    def command_get_toc(self, param):
        """
        Get the table of contents of a course.
        """
        course = self.parse_course_request(param)
        if course:
            print(course.course_TOC)

    def command_get_transcript(self, param):
        """
        Get the transcript of a course.
        """
        course = self.parse_course_request(param)
        if course:
            print(course.course_transcript)

    def command_get_url(self, param):
        """
        Get the URL of a course.
        """
        course = self.parse_course_request(param)
        if course:
            print(course.metadata["Course URL"])

    def command_curate(self, param):
        """
        Similarity search courses by a query string.
        """
        query = param
        print(Curate(query))

    def command_mentor(self, param):
        """
        Have a Mentor generate a Curation.
        """
        query = param
        mentor = Mentor(query)
        if mentor:
            print(mentor.courses)

    ## Our functions for building / editing curations
    def command_view_curation(self):
        """
        View the current curation, with numbers.
        """
        numbered_curation = self.number_courses()["curation"]
        for number, course in numbered_curation:
            print(f"{number}. {course}")

    def command_view_curation_duration(self):
        """
        View the duration of the current curation.
        """
        if not self.curation:
            self.console.print("No curation.")
            return
        duration = self.curation.duration
        print(duration)

    def command_add_course(self, param):
        """
        Add a course to the curation.
        """
        if not self.curation:
            self.curation = Curation(title=None, courses=[])
        course = self.parse_course_request(param)
        if course:
            self.curation.courses.append(course)

    def command_remove_course(self, param):
        """
        Remove a course from the curation.
        """
        if not self.curation:
            self.console.print("No curation.")
            return
        course = self.parse_course_request(param)
        if course:
            self.curation.courses.remove(course)

    def command_clear_curation(self):
        """
        Clear the current curation.
        """
        self.curation = None

    def command_save_curation(self, param):
        """
        Save the current curation to a file.
        """
        filename = param
        # prompt user for curation title
        # save curation to file
        pass

    def command_build_learningpath(self, param):
        """
        Build a Learning Path from the current curation.
        """
        if self.curation:
            self.curation.title = param
            # prompt user for curation title
            learning_path = build_LearningPath_from_Curation(self.curation)
            print(learning_path)
        else:
            self.console.print("No curation.")

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

    def command_consult_lnd(self, param):
        """
        Have an L&D expert critique the curation. Need to pass an audience param.
        """
        audience = param
        if not self.curation:
            self.console.print("No curation.")
            return
        review = review_curriculum(
            curation=self.curation, audience=audience, model=self.model
        )
        return review

    def command_consult_learner(self, param):
        """
        Have a learner provide feedback on the curation. Need to pass an audience param.
        """
        audience = param
        if not self.curation:
            self.console.print("No curation.")
            return
        feedback = learner_progression(
            curation=self.curation, audience=audience, model=self.model
        )
        return feedback

    def command_consult_audience(self):
        """
        Classify the audience for the curation.
        """
        if not self.curation:
            self.console.print("No curation.")
            return
        audience = classify_audience(curation=self.curation, model=self.model)
        return audience

    def command_title_certificate(self):
        """
        Title the certificate for the curation. This will also guess a partner.
        """
        if not self.curation:
            self.console.print("No curation.")
            return
        title = title_certificate(curation=self.curation, model=self.model)
        return title

    def command_suggest_partner(self):
        """
        For the current curation, suggest a partner.
        """
        pass

    ## Our commands for managing the workspace
    def command_view_workspace(self):
        """
        View the workspace, with numbers.
        """
        # Numbers start in the Curation, then the Workspace.
        pass

    def command_add_workspace(self, param):
        """
        Add a course to the workspace.
        """
        course = self.parse_course_request(param)
        pass

    def command_remove_workspace(self, param):
        """
        Remove a course from the workspace.
        """
        course = self.parse_course_request(param)
        pass

    def command_clear_workspace(self):
        """
        Clear the workspace.
        """
        pass

    ## Our commands for managing the blacklist
    def command_view_blacklist(self):
        """
        View the blacklist.
        """
        pass

    def command_clear_blacklist(self):
        """
        Clear the blacklist.
        """
        pass

    def command_add_blacklist(self, param):
        """
        Add a course to the blacklist.
        """
        course = self.parse_course_request(param)
        pass

    def command_remove_blacklist(self, param):
        """
        Remove a course from the blacklist.
        """
        course = self.parse_course_request(param)
        pass


if __name__ == "__main__":
    model = Model("claude")
    chat = MentorChat(model)
    chat.chat()
