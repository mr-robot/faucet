import uuid


class Message(object):
    def __init__(self, original_message_contents):
        self.original_message_contents = original_message_contents
        self.uuid = uuid.uuid4()
        self.path = None

        self.ref = {}

    def add_reference(self, key, reference):
        self.ref[key] = reference


class MultiMessage(Message):
    def __init__(self, original_message_contents_collection):
        super(MultiMessage, self).__init__(original_message_contents_collection)

        self.messages = self.add_messages(original_message_contents_collection)

    def add_messages(self, original_message_contents):
        messages = []
        for original in original_message_contents():
            messages.append(Message(original))

        return messages

