

def help_reply():
    with open("txt/help.txt", "r", encoding="utf-8") as file:
        return file.read()

def about_reply():
    with open("txt/about.txt", "r", encoding="utf-8") as file:
        return file.read()

def gyde_reply():
    with open("txt/gyde.txt", "r", encoding="utf-8") as file:
        return file.read()