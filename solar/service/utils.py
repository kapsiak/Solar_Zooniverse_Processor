def build_from_defaults(default_list, new_list):
    ret = []
    for i in default_list:
        search = [x for x in new_list if x.name == i.name]
        if search:
            ret.append(search[0])
        else:
            ret.append(i)
    return ret
