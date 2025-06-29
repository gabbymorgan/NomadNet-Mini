import nomadnet

class Component:
    def __init__(self, parent=None):
        self.app = nomadnet.NomadNetworkApp.get_shared_instance()
        self.parent = parent

        if self.parent:
            self.ui = parent.ui
        
    def start(self):
        self.update()
    
    def update(self):
        return
