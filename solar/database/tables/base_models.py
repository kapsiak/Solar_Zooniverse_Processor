import peewee as pw
from solar.database.database import database as db
from pathlib import Path
from solar.common.utils import checksum
import shutil
from typing import Union


class Base_Model(pw.Model):
    """
    Base class for database models
    """

    class Meta:
        database = db


class File_Model(Base_Model):
    """
    A wrapper class for files. Includes methods to hash the contents of file, and then later verify its integrity.
    """

    file_path = pw.CharField(
        default="NA", unique=True
    )  # The location of the file on the disk
    file_name = pw.CharField(default="NA")  # The name of the file
    file_hash = pw.CharField(default="NA")  # The file checksum

    def get_hash(self) -> str:
        """
        Compute the hash of the file.
        Also sets the self.file_hash variable

        :return: The checksum
        :rtype: str
        """
        try:
            self.file_hash = checksum(self.file_path)
        except IOError as e:
            print(f"Could not get hash: {e}")
            self.file_hash = "NA"
        self.save()
        return self.file_hash

    def check_integrity(self) -> bool:
        """
        See if the current contents of the file match the checksum

        :return: True if the checksum of the file matches the one saved in self.file_hash, otherwise false
        :rtype: bool
        """
        p = Path(self.file_path)
        if p.is_file():
            if checksum(self.file_path) == self.file_hash:
                return True
        return False

    def make_path(self, default_form=None):
        pass

    def export(self, new_path: Union[str, Path]):
        """
        Create a copy of this file at a given path.

        :param new_path: The location of the new file
        :type new_path: Union[str, Path]
        """
        new = Path(new_path)

        if new.is_dir():
            new = new / Path(self.file_path).name

        new.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy(self.file_path, new)
            return new
        except IOError as e:
            print(e)
        except Exception as e:
            print(e)
        return False
