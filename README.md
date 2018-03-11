# stranger-things-story-map

Convert each YAML file into a GraphViz file and render the graph with dot.
This can be done by running vizepisode.py with the --render option,
> python vizepisode.py --render season_1_chapter_1.yml

or piecewise, using dot:
> python vizepisode.py season_1_chapter_1.yml
> dot -Tsvg season_1_chapter_1.dot -o season_1_chapter_1.dot.svg
