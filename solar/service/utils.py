def build_from_defaults(default_list, new_list):
    ret = []
    for i in default_list:
        search = [x for x in new_list if x.name == i.name]
        if not search:
            ret.append(i)
    ret.extend(new_list)
    return ret
