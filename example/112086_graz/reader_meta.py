import re

d = {}
fn = 'Stammdaten-112086.txt'
fn = 'meta.txt'
with open(fn, 'r', encoding='utf8') as f:
    is_table = False
    main_key = None
    table_keys = None

    for line in f.readlines():
        if line.strip() == '':
            continue

        line = line.replace(';', '')

        if is_table and (':' in line):
                is_table = False
                main_key = None

        if (line.count(':') == 1) and line.strip().endswith(':'):
            main_key = line.split(':')[0].strip()
            d[main_key] = list()

        elif (line.count(':') == 1) and not line.strip().endswith(':'):
            args = line.strip().split(':')
            key = args[0].strip()
            if key in d:
                if isinstance(d[key], str):
                    d[key] = [d[key]]
                d[key].append(args[1].strip())
            else:
                d[key] = args[1].strip()

        elif line.count(':') > 1:
            if (line.count(':  ') == (line.count(':') - 1)) and line.strip().endswith(':'):
                is_table = True

                if main_key is None:
                    main_key = line.split(':')[0].strip()
                    d[main_key] = list()

                # d[main_key] += line
                table_keys = [k.strip() for k in line.split(':')[:line.count(':')]]
            elif line.strip().endswith(':'):
                main_key = line.split(':')[0].strip()
                d[main_key] = list()
            else:
                args = line.strip().split(':')
                key = args[0].strip()
                value = ':'.join(args[1:]).strip()
                if key in d:
                    if isinstance(d[key], str):
                        d[key] = [d[key]]
                    d[key].append(value)
                else:
                    d[key] = value

        elif is_table:
            table_values = dict(zip(table_keys, [v.strip() for v in re.split(r'\s\s+', line.strip())]))
            d[main_key].append(table_values)

        else:
            # last_args key
            d[args[0].strip()] = [args[1].strip(), line.strip()]

# import json
# json.dump(d, open(fn.replace('.txt', '.json'), 'w', encoding='utf8'), indent=4, ensure_ascii=False)
import yaml
yaml.dump(d, open(fn.replace('.txt', '.yaml'), 'w'), default_flow_style=False, sort_keys=False, allow_unicode=False)
