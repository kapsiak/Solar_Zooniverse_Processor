import peewee as pw
from solar.database.database import database as db
from pathlib import Path
from solar.common.utils import checksum
import shutil
from typing import Union
from solar.database.utils import dbformat, dbpathformat
from solar.common.config import Config


class Base_Model(pw.Model):
    """
    Base class for database models
    """

    class Meta:
        database = db


class PathField(pw.Field):
    field_type = "text"

    def db_value(self, value):
        """Function db_value: Convert path into something text that may be stored in the database
        
        :param value: the path
        :type value: Path
        :returns: str(path)
        :type return: str
        """
        return str(value)

    def python_value(self, value):
        """Function python_value: Convert the text in the database back into a path
        
        :param value: the database text
        :type value: str
        :returns: Path(str)
        :type return: Path
        """
        return Path(value)


class File_Model(Base_Model):
    """
    A wrapper class for files. Includes methods to hash the contents of file, and then later verify its integrity.
    """

    file_path = PathField(
        default="NA", unique=True
    )  # The location of the file on the disk
    file_name = PathField(default="NA")  # The name of the file
    file_hash = pw.CharField(default="NA")  # The file checksum

    def rename(self, file_name_format=None, file_path_format=None, *args, **kwargs):
        """Function rename: Rename a file within the database, and move it to the new location

        The format strings may use any parameters, provided that they appear either in one of the dict-like object or classes passed to *args,
        or as one of the kwargs.

        file_path_format takes the special argument "ffilename" which is the result, after formatting, of file_name_format.

        :param file_name_format: The format to use for the name of the file, defaults to None
        :type file_name_format: str
        :param file_path_format: The format to use for the path, defaults to None
        :type file_path_format: str
        :param *args: List of dictionary-like objects
        :type *args: List[dict]
        :returns: None
        :type return: None
        """
        if not file_name_format:
            file_name_format = self.file_name_format
        if not file_path_format:
            file_path_format = self.file_path_format

        old_path = self.file_path
        self.file_path = dbpathformat(
            file_name_format, file_path_format, *args, **kwargs
        )
        self.file_name = dbformat(file_name_format, *args, **kwargs)

        p = Path(self.file_path)
        p.parent.mkdir(parents=True, exist_ok=True)

        self.save()

        shutil.move(old_path, self.file_path)

    def get_hash(self):
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

    def check_integrity(self):
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

    def update_single(self):
        raise NotImplementedError

    @staticmethod
    def update_table():
        raise NotImplementedError

    def export(self, new_path):
        """
        Create a copy of this file at a given path.

        :param new_path: The location of the new file
        :type new_path: Path-like
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
