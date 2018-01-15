import argparse
import yaml
from graphviz import Digraph

def keyify(name):
    return name.replace('.', '').replace(' ', '_')

parser = argparse.ArgumentParser(
    description='Take a YAML file representing an episode '
                'and translate it to a Graphviz DOT file '
                'which can then be rendered.')
parser.add_argument('input', nargs='+', help='file(s) to translate')
args = parser.parse_args()

for filename in args.input:
    with open(filename, 'r') as yaml_f:
        episode = yaml.load(yaml_f)

    epoch_keys = []
    character_keys = {}

    dot = Digraph(comment=episode['title'])
    dot.attr(center='1', randir='TB')
    dot.attr('edge', dir='none')
    dot.attr('node', width='0.3', height='0.3')

    timeline = Digraph(name='timeline')
    timeline.attr('node', style='invis', label='')
    timeline.attr('edge', style='invis')
    for epoch in episode['scenes']:
        for key in epoch.keys():
            key = keyify(key)
            epoch_keys.append(key)
            timeline.node(key)
    dot.subgraph(timeline)

    for epoch in episode['scenes']:
        for key, scenes in epoch.items():
            key = keyify(key)
            epoch = Digraph(name='cluster_%s' % key)
            for i, scene in enumerate(scenes):
                scene_key = '%s_%d' % (key, i) 
                scene_cluster = Digraph(name='cluster_%s' % scene_key)
                scene_cluster.attr(label='%s: %s' % (scene['location'], scene['title']))
                if 'characters' in scene:
                    for character in scene['characters']:
                        if character not in character_keys:
                            character_keys[character] = []
                        character_key = keyify(character)+'_'+scene_key
                        character_keys[character].append(character_key)
                        scene_cluster.node(character_key)
                epoch.subgraph(scene_cluster)
            dot.subgraph(epoch)

    for character_name, character_key_list in character_keys.items():
        character_cluster = Digraph()
        character_cluster.attr(label=character_name)
        for character_key in character_key_list:
            character_cluster.node(character_key)
        dot.subgraph(character_cluster)

    # finish here

    with open(filename.replace('.yml', '-test.dot'), 'w') as dot_f:
        dot_f.write(str(dot))
