with open('README.md', 'r') as f:
    s = f.read()
    s = s.replace('](ehyd_tools', '](https://github.com/MarkusPic/ehyd_tools/tree/master/ehyd_tools')
    s = s.replace('](example', '](https://github.com/MarkusPic/ehyd_tools/tree/master/example')
with open('README_github.md', 'w') as f:
    f.write(s)
