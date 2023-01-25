with open("map.tmx", mode='r', encoding='utf-8') as map:
    lines = map.readlines() 
    refactor_lines = []
    for i in lines:
        refactor_i = i
        if 'visible' in i:
            refactor_i = ''
        refactor_lines.append(refactor_i)

with open('map.tmx', mode='w', encoding='utf-8') as new_map:
    new_map.write(''.join(refactor_lines))

