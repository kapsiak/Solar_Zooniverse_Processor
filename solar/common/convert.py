import ast


def __scalar_convert(val, ftype, datetime=None):
    if ftype == "str":
        return val
    elif ftype == "int":
        return int(val)
    elif ftype == "float":
        return float(val)
    elif ftype == "datetime":
        return datetime.strptime(val, datetime)
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
                raise NoFormat
            else:
                field_type = main_type
                ret_str = datetime.strptime(value, data_format)
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
