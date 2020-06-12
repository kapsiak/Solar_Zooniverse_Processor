class Attribute:
    def __init__(self,name,value, query_name=None):
        self.query_name = query_name if query_name else name
        self.name = name
        self.value = value

    def get_value(self):
        if type(self.value) == list:
            return ','.join(self.value)
        else:
            return self.value
        

    def __eq__(self,other):
        if type(other) is str:
            return self.name == other
        else:
            return (self.name,self.value) == (other.name,other.value)
    


    
