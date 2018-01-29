'''
This script converts an episode YAML file into a GraphViz file and optionally
renders that file with 'dot'.

Example usage:
> python vizepisode.py --render season_1_chapter_1.yml

This is equivalent to:
> python vizepisode.py season_1_chapter_1.yml
> dot -Tsvg season_1_chapter_1.dot -o season_1_chapter_1.dot.svg

'''

import argparse
import yaml
from graphviz import Digraph
from textwrap import wrap

def keyify(name):
    return name.replace('.', '').replace(' ', '_')

def titlewrap(string):
    return '\n'.join(wrap(string, 40))

parser = argparse.ArgumentParser(
    description='Take a YAML file representing an episode '
                'and translate it to a Graphviz DOT file '
                'which can then be rendered.')
parser.add_argument('input', nargs='+', help='file(s) to translate')
parser.add_argument('--character-file', nargs=1,
                    default='characters.yml',
                    help='character reference file')
parser.add_argument('--render', default=False, action='store_true')
args = parser.parse_args()

character_map = None
with open(args.character_file, 'r') as char_f:
    character_map = {}

for filename in args.input:
    with open(filename, 'r') as yaml_f:
        episode = yaml.load(yaml_f)

    epoch_keys = []
    character_keys = {}

    dot = Digraph(comment=episode['title'],
                  format='svg')
    dot.attr(center='1', randir='TB')
    dot.attr('edge', dir='none')
    dot.attr('node', width='0.3', height='0.3')

    timeline = Digraph(name='timeline')
    timeline.attr('node', style='invis', label='')
    timeline.attr('edge', style='invis')
    last_epoch = None
    for epoch in episode['scenes']:
        for key in epoch.keys():
            key = keyify(key)
            epoch_keys.append(key)
            #timeline.node(key)
        if last_epoch:
            timeline.edge(last_epoch, key)
        last_epoch = key
    dot.subgraph(timeline)

    for epoch in episode['scenes']:
        for key, scenes in epoch.items():
            key = keyify(key)
            for i, scene in enumerate(scenes):
                scene_key = '%s_%d' % (key, i)
                if 'characters' in scene:
                    for character in scene['characters']:
                        if character not in character_keys:
                            character_keys[character] = []
                        character_key = keyify(character)+'_'+scene_key
                        character_keys[character].append(character_key)

    character_definitions = Digraph(comment='Styles for Character Nodes')
    character_definitions.attr('node', colorscheme='dark28',
                               shape='box', style='rounded')
    character_definitions.attr('edge', colorscheme='dark28')
    color_index = 0
    for character_name, character_key_list in character_keys.items():
        character_cluster = Digraph()
        if character_map:
            character_name = character_map[character_name]
        character_cluster.attr('node', color=str((color_index % 8) + 1),
                               label=character_name)
        character_cluster.attr('edge', color=str((color_index % 8) + 1))
        color_index += 1
        last_character_key = None
        if len(character_key_list) == 1:
            character_cluster.node(character_key_list[0])
        else:
            for character_key in character_key_list:
                if last_character_key:
                    character_cluster.edge(last_character_key, character_key)
                last_character_key = character_key
        character_definitions.subgraph(character_cluster)
    dot.subgraph(character_definitions)

    for epoch in episode['scenes']:
        for key, scenes in epoch.items():
            key = keyify(key)
            epoch = Digraph(name='cluster_%s' % key)
            epoch.node(key)
            for i, scene in enumerate(scenes):
                scene_key = '%s_%d' % (key, i)
                scene_cluster = Digraph(name='cluster_%s' % scene_key)
                scene_cluster.attr(label=titlewrap('%s: %s' % (scene['location'], scene['title'])))
                if 'characters' in scene:
                    for character in scene['characters']:
                        character_key = keyify(character)+'_'+scene_key
                        scene_cluster.node(character_key)
                epoch.subgraph(scene_cluster)
            dot.subgraph(epoch)

    outfilename = filename.replace('.yml', '.dot')

    if args.render:
        dot.render(outfilename)
    else:
        dot.save(outfilename)
