def flatten_list(data):
    lst = []

    for element in data:
        if type(element) == list:
            flatten_list(element)
        else:
            lst.append(element)

    return lst
