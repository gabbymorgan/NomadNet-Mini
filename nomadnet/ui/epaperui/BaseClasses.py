class Component:
    def __init__(self, app, parent=None):
        self.app = app
        self.parent = parent

        if self.parent:
            self.ui = parent.ui
        
    def start(self):
        self.update()
    
    def update(self):
        return
