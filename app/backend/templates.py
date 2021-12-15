from backend.models import Template


class Messages():
    START_COMMAND_CHAT = Template.messages.get(id=4)
    START_COMMAND_PRIVATE = Template.messages.get(id=5)
    JOINED = Template.messages.get(id=9)
    LEAVE = Template.messages.get(id=12)
    TRUTH_OR_DARE = Template.messages.get(id=13)
    NOT_JOINED = Template.messages.get(id=16)
    JOINED_PRIVATE = Template.messages.get(id=17)
    JOINED_ALREADY_PRIVATE = Template.messages.get(id=18)
    TASK_DARE = Template.messages.get(id=21)
    TASK_TRUTH = Template.messages.get(id=22)


class Keys():
    fdvd = Template.keys.get(id=1)
    ADD_TO_CHAT = Template.keys.get(id=6)
    JOIN = Template.keys.get(id=7)
    START_GAME = Template.keys.get(id=8)
    LEAVE = Template.keys.get(id=11)
    TRUTH = Template.keys.get(id=14)
    DARE = Template.keys.get(id=15)
    RETURN_TO_CHAT = Template.keys.get(id=19)
    TASK_COMPLETED = Template.keys.get(id=20)


class Smiles():
    fgthth = Template.smiles.get(id=3)
