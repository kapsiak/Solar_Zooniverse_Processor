# Currently unused
class AlreadyExists(Exception):
    def __init__(self, row: Any):
        self.row = row

    def __repr__(self):
        return f"<AlreadyExists: {self.row}>"

    def __str__(self):
        return f"Row {self.row} is already in table {type(self.row)}"
