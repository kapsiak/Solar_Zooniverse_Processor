def format_string(format_string, row,**kwargs):
    return format_string.format(**row.__data__,**kwargs)
