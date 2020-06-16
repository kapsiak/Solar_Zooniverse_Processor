import peewee as pw
from solar.database.database import database as db
from pathlib import Path
from solar.common.utils import checksum


class Base_Model(pw.Model):
    @classmethod
    def update_table(cls):
        pass

    def check_and_save(self):
        try:
            self.save()
            return True
        except pw.IntegrityError as e:
            print(e)
            return False

    class Meta:
        database = db


class File_Model(Base_Model):

    file_path = pw.CharField(default="NA")
    file_hash = pw.CharField(default="NA")
    file_name = pw.CharField(default="NA")

    def correct_file_path(self):
        pass

    @classmethod
    def correct_path_database(cls):
        for f in cls.select():
            f.correct_file_path()

    def get_hash(self):
        try:
            self.file_hash = checksum(self.file_path)
        except IOError as e:
            print(f"Could not get hash: {e}")
            self.file_hash = "NA"
        self.save()
        return self.file_hash

    def check_integrity(self):
        p = Path(self.file_path)
        if p.is_file():
            if checksum(self.file_path) == self.file_hash:
                return True
        return False
