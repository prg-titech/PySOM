from som.vmobjects.object import Object

class Integer(Object):
    
    def __init__(self, nilObject):
        super(Integer, self).__init__(nilObject)
        self._embedded_integer = 0
    
    def get_embedded_integer(self):
        return self
    
    def set_embedded_integer(self, value):
        self._embedded_integer = value
    
    def __str__(self):
        return str(self._embedded_integer)