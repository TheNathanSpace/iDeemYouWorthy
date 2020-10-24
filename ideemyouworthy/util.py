def dictToSet(dict_to_convert):
    returned_set = set()
    for key in dict_to_convert:
        returned_set.add(key)
    return returned_set
    
def dictToSetValues(dict_to_convert):
    returned_set = set()
    for key in dict_to_convert:
        returned_set.add(dict_to_convert[key])
    return returned_set