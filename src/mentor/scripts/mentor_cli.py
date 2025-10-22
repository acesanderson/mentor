from mentor.agentic.mentor_chat import MentorChat, Model


def main():
    model = Model("claude")
    chat = MentorChat(model)
    chat.chat()


if __name__ == "__main__":
    main()
