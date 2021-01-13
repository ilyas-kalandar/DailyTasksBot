class Task:
    """ A class for implementing Task"""

    def __init__(self, user_id, name, is_completed):
        self.user_id = user_id
        self.name = name
        self.is_completed = is_completed


class User:
    def __init__(self, user_id, notifies, extend_task, progress, days):
        self.user_id = user_id
        self.notifies = notifies
        self.extend_task = extend_task
        self.progress = progress
        self.days = days
