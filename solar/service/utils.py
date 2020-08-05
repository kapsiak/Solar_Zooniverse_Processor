def build_from_defaults(default_list, new_list):
    """Function build_from_defaults: A utility function for "merging" two attribute lists.

    Effectively join the two lists, giving priority to the elements of new_list
    
    :param default_list: The of "default" attributes
    :type default_list: List[Attribute]
    :param new_list: List of the attributes to add to the result 
    :type new_list: List[Attribute]
    :returns: New list created by combining the inputs
    :type return: List[Attribute]
    """
    ret = []
    for i in default_list:
        search = [x for x in new_list if x.name == i.name]
        if not search:
            ret.append(i)
    ret.extend(new_list)
    return ret
