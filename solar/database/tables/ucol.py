"""
This module is designed to implement a naive "union" type sqlite column for storing fits_headers. 
"""

import peewee as pw
from .base_models import Base_Model
from datetime import datetime
from functools import wraps


class NoFormat(Exception):
    def __init__(self, val=None):
        self.str = f"Trying to format {val}"

    def __str__(self):
        return self.str


def get_type(value, data_format=None):
    """Function get_type: Get the type of a value
    
    :param value: the value to insect
    :type value: any
    :param data_format: str, defaults to None
    :type data_format: str
    :returns: The type and subtype
    :type return: (str,str)
    """
    field_type = None
    subtype = None
    field_type = value.__class__.__name__
    if field_type == "list" and value:
        sub_type = str(type(value[0]))
        subtype = sub_type
    else:
        subtype = None
    return (field_type, subtype)


class UnionCol(Base_Model):
    """
    A table designed to hold different types.
    """

    # The table to store the elements of lists
    list_storage_table = None

    _field_type = pw.CharField(column_name="type")
    _subtype = pw.CharField(null=True, column_name="subtype")
    _format = pw.CharField(null=True, column_name="format")

    _value_string = pw.CharField(null=True, column_name="string")
    _value_datetime = pw.DateTimeField(null=True, column_name="datetime")
    _value_int = pw.IntegerField(null=True, column_name="integer")
    _value_float = pw.FloatField(null=True, column_name="float")

    @property
    def field_type(self):
        return self._field_type

    @field_type.setter
    def field_type(self, val):
        if val not in ["list", "int", "float", "datetime", "str"]:
            raise ValueError

    @property
    def subtype(self):
        return self._subtype

    @subtype.setter
    def subtype(self, val):
        if val not in ["list", "int", "float", "datetime", "str"]:
            raise ValueError

    @property
    def format(self):
        return self._format

    @format.setter
    def format(self, value):
        self._format = value

    @property
    def value(self):
        if self._field_type == "int":
            return self._value_int
        elif self._field_type == "float":
            return self._value_float
        elif self._field_type == "datetime":
            return self._value_datetime
        elif self._field_type == "str":
            return self._value_string
        elif self._field_type == "list":
            if self in self.__class__:
                # Has the object been saved?
                return [x.value for x in self.list_values]
            elif hasattr(self, "list_refs"):
                return [x.value for x in self.list_refs]
            else:
                raise ValueError

    @value.setter
    def value(self, value):
        self._field_type, self._subtype = get_type(value)
        if self._field_type == "int":
            self._value_int = value
        elif self._field_type == "float":
            self._value_float = value
        elif self._field_type == "datetime":
            self._value_datetime = value
        elif self._field_type == "str":
            self._value_string = value
        elif self._field_type == "list":
            self.list_refs = []
            for val in value:
                new = self.list_storage_table(table=self, _format=self._format)
                new.value = val
                self.list_refs.append(new)

    def save(self, *args, **kwargs):
        x = super(UnionCol, self).save(*args, **kwargs)
        if hasattr(self, "list_refs"):
            for val in self.list_refs:
                val.save()
        return x


class List_Storage(UnionCol):
    table = pw.ForeignKeyField(UnionCol, backref="list_values")

    def __str__(self):
        return """
        id = {self.id}
        table = {self.table}
        val = {self.value}
        type = {self._field_type}
        stype = {self._subtype}
            """
