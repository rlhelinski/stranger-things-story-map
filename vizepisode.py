import argparse
import yaml
from graphviz import Digraph

parser = argparse.ArgumentParser(
    description='Take a YAML file representing an episode '
                'and translate it to a Graphviz DOT file '
                'which can then be rendered.')
parser.add_argument('input', nargs='+', help='file(s) to translate')
args = parser.parse_args()

for filename in args.input:
    with open(filename, 'r') as yaml_f:
        episode = yaml.load(yaml_f)

    dot = Digraph(comment=episode['title'])

    timeline = Digraph()
    for epoch in episode['scenes']:
        for key in epoch.keys():
            timeline.node(key.replace(' ', '_'))
    dot.subgraph(timeline)

    with open(filename.replace('.yml', '-test.dot'), 'w') as dot_f:
        dot_f.write(str(dot))
