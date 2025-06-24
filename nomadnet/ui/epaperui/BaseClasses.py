class Component:
    def __init__(self, app, parent=None):
        self.app = app
        self.parent = parent

        if self.parent:
            self.ui = parent.ui
        

