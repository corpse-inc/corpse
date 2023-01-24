with open("map - Copy.txt", mode='r', encoding='utf-8') as map: 
    lines = map.readlines() 
    refactor_lines = []
    for i in lines:
        refactor_i = i
        if 'visible' in i:
            refactor_i = i[0:i.rfind('visible') - 1] + '/>'     
        refactor_lines.append(refactor_i)

with open('rafctor map.txt', mode='w', encoding='utf-8') as new_map:
    new_map.write(''.join(refactor_lines))
