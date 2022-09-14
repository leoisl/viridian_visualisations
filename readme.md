# Viridian Visualisation

Creates `gisaid` vs `viridian` `taxonium` trees visualisation like this: [examples/final.mp4](examples/final.mp4)

## Walkthrough

1. Get the `taxonium` tree drawings for both `gisaid` and `viridian`:

```
python get_taxonium_screenshots_from_trees.py --gisaid_tree gisaid_illumina.opt.taxonium.jsonl.gz --viridian_tree viridian_illumina.opt.taxonium.jsonl.gz --output_dir vis_out --small_test
```

2. Create video with pauses for the trees drawings:

```
python make_video_from_screenshots.py --gisaid_dir vis_out/vis_gisaid --viridian_dir vis_out/vis_viridian --output_dir vis_both --pause_file examples/pauses.txt
```

## Usage

### `get_taxonium_screenshots_from_trees.py`
```
usage: get_taxonium_screenshots_from_trees.py [-h] --gisaid_tree GISAID_TREE --viridian_tree VIRIDIAN_TREE --output_dir OUTPUT_DIR [--small_test]

Upload trees to https://taxonium.org/ and save their visualisations

optional arguments:
  -h, --help            show this help message and exit
  --gisaid_tree GISAID_TREE
  --viridian_tree VIRIDIAN_TREE
  --output_dir OUTPUT_DIR
  --small_test          Save just a small number of trees instead of all, for testing

```

### `make_video_from_screenshots.py`

```
usage: make_video_from_screenshots.py [-h] --gisaid_dir GISAID_DIR --viridian_dir VIRIDIAN_DIR [--pause_file PAUSE_FILE] [--framerate FRAMERATE] --output_dir
                                      OUTPUT_DIR

Build a video from screenshots previously captured from get_taxonium_screenshots_from_trees.py

optional arguments:
  -h, --help            show this help message and exit
  --gisaid_dir GISAID_DIR
  --viridian_dir VIRIDIAN_DIR
  --pause_file PAUSE_FILE
                        Specifies a path to a file where each line specifies where and for how long to pause. Each pause is described by one line such as: ORF1b[5] 3
                        to pause the video at gene ORF1b residue 5 for 3 seconds.
  --framerate FRAMERATE
  --output_dir OUTPUT_DIR
```