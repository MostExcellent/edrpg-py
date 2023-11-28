import json
# Character Sheet
class Character():
    # Open skills.json
    def __init__(self):
        # Load skills from json
        self.skills = {}
        with open('skills.json') as f:
            skills = json.load(f)
        for skill in skills:
            self.skills[skill] = 10