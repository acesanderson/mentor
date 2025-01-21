"""
Rough draft of a chatbot for building curations.
TODO:
- use a simple list for self.curation
- user can "bless" curation into a Curation object, giving it a title.
- user can generate LP from Curation object
"""

from Chain import Chat, Model
from Curator import Curate
from Kramer import Course, Get, Curation, LearningPath, build_LearningPath_from_Curation
from Mentor import Mentor


class MentorChat(Chat):
    def __init__(self, model):
        # Access the self.one_param_commands from parent class
        super().__init__(model)
        self.welcome_message = "[green]Hello! Let's build a Curation together.[/green]"
        self.one_param_commands.append("query")  # Query a single string
        self.two_param_commands.append("get")
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
        workspace_courses = self.workspace
        # First, number the courses in the curation
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
    def command_get_course(self, param):
        """
        Get a course by the course ID.
        """
        course = self.parse_course_request(param)
        if course:
            print(course)

    def command_get_description(self, param):
        """
        Get the description of a course.
        """
        course = self.parse_course_request(param)
        if course:
            print(course.metadata["Course Description"])

    def command_get_metadata(self, param):
        """
        Get the metadata of a course.
        """
        course = self.parse_course_request(param)
        if course:
            print(course.metadata)

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
        duration = self.curation.duration
        print(duration)

    def command_add_course(self, param):
        """
        Add a course to the curation.
        """
        course = self.parse_course_request(param)
        if course:
            self.curation.courses.append(course)

    def command_remove_course(self, param):
        """
        Remove a course from the curation.
        """
        course = self.parse_course_request(param)
        if course:
            self.curation.courses.remove(course)

    def command_clear_curation(self):
        """
        Clear the current curation.
        """
        self.curation = []

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
        title = param
        # prompt user for curation title
        learning_path = build_LearningPath_from_Curation(self.curation, title)
        print(learning_path)

    ## LLMs! Our special prompt functions
    def command_query_curation(self):
        """
        Ask a question about the curation. This uses titles + descriptions.
        """
        pass

    def command_query_TOCs(self):
        """
        Ask a question about the combined TOCs of the curation.
        """
        pass

    def command_query_transcript(self, param):
        """
        Use a local model to query the transcript of a course.
        """
        course = self.parse_course_request(param)
        pass

    def command_review_curation(self):
        """
        Have an L&D expert critique the curation.
        """
        pass

    def command_learner_feedback(self):
        """
        Have a learner provide feedback on the curation.
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
    model = Model("gpt")
    chat = MentorChat(model)
    chat.chat()
