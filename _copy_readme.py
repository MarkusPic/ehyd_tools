with open('README.md', 'r') as f:
    s = f.read()
    s = s.replace('](ehyd_tools', '](https://github.com/MarkusPic/ehyd_tools/blob/master/ehyd_tools')
    s = s.replace('](example/ehyd_112086_plot.png)', '](https://github.com/MarkusPic/ehyd_tools/raw/master/example/5214_design_rainfall_plot.png)')
    s = s.replace('](example', '](https://github.com/MarkusPic/ehyd_tools/blob/master/example')
with open('README_github.md', 'w') as f:
    f.write(s)
