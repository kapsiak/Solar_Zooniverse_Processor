import ast
from datetime import datetime


class NoFormat(Exception):
    def __init__(self, val=None):
        self.str = f"Trying to format {val}"

    def __str__(self):
        return self.str


def __scalar_convert(val, ftype, t_format=None):
    if ftype == "str":
        return val
    elif ftype == "int":
        return int(val)
    elif ftype == "float":
        return float(val)
    elif ftype == "datetime":
        return datetime.strptime(val, t_format)
    else:
        return None


def data_to_string(value, data_format=None):
    ret_str = ""
    field_type = None
    subtype = None
    if not isinstance(value, str):
        main_type = value.__class__.__name__
        if main_type == "list" and value:
            sub_type = value[0].__class__.__name__
            field_type = main_type
            subtype = sub_type
            ret_str = ",".join([str(x) for x in value])
        elif main_type in ["float", "int"]:
            field_type = main_type
            ret_str = str(value)
        elif main_type == "datetime":
            if not data_format:
                raise NoFormat(value)
            else:
                field_type = main_type
                ret_str = datetime.strftime(value, data_format)
        else:
            raise ValueError
    else:
        try:
            to_data = ast.literal_eval(value)
        except ValueError:
            to_data = ast.literal_eval(f'"{value}"')
        except SyntaxError:
            to_data = value

        if isinstance(to_data, str):
            ret_str = to_data
            field_type = "str"
        else:
            (ret_str, field_type, subtype) = data_to_string(to_data, data_format)
    return (ret_str, field_type, subtype)


def string_to_data(str_val, main_type, subtype=None, data_format=None):
    if main_type == "list":
        if not subtype:
            raise ValueError
        return [__scalar_convert(x, subtype, data_format) for x in str_val.split(",")]
    else:
        return __scalar_convert(str_val, main_type, data_format)
