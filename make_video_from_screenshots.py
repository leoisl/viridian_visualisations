import ffmpeg
from pathlib import Path
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import argparse
import logging
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)


def get_args():
    parser = argparse.ArgumentParser(description="Build a video from screenshots previously captured from get_taxonium_screenshots_from_trees.py")

    parser.add_argument('--gisaid_dir')
    parser.add_argument('--viridian_dir')
    parser.add_argument('--pause_file', default=None,
                        help="Specifies a path to a file where each line specifies where and for how long to pause. "
                             "Each pause is described by one line such as: ORF1b[5] 3 to pause the video at "
                             "gene ORF1b residue 5 for 3 seconds.")
    parser.add_argument("--framerate", default=10)
    parser.add_argument('--output_dir')
    args = parser.parse_args()
    return args


# from https://note.nkmk.me/en/python-pillow-concat-images/
def concatenate_horizontally(im1, im2):
    dst = Image.new('RGB', (im1.width + im2.width, im1.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    return dst


def get_gene_residue_from_filename(filename):
    split_label = filename.replace(".png", "").split("_")
    gene, residue = split_label[1], split_label[3]
    return gene, residue


def add_label(image, label, top_padding, tree_title_1, tree_title_2):
    dst = Image.new('RGB', (image.width, image.height+top_padding))
    dst.paste(image, (0, top_padding))
    draw = ImageDraw.Draw(dst)
    draw.rectangle((0, 0, image.width, top_padding), fill=(255, 255, 255), outline=(255, 255, 255))
    large_font = ImageFont.truetype("resources/fonts/arial/arial.ttf", 30)
    small_font = ImageFont.truetype("resources/fonts/arial/arial.ttf", 18)
    gene, residue = get_gene_residue_from_filename(label)
    draw.text((30, 5), f"{gene}[{residue}]", (0, 0, 0), font=large_font)
    draw.text((10, 60), tree_title_1, (0, 0, 0), font=small_font)
    draw.text((image.width//2+30, 60), tree_title_2, (0, 0, 0), font=small_font)
    return dst


def get_pauses(pause_file):
    locus_to_seconds = {}

    if pause_file is None:
        return locus_to_seconds

    with open(pause_file) as pause_fh:
        for line in pause_fh:
            line = line.strip()
            if len(line) > 0:
                locus, seconds = line.split()
                seconds = int(seconds)
                locus_to_seconds[locus] = seconds
    return locus_to_seconds


def get_set_of_genes_to_draw(combined_pngs_dir):
    genes = set()
    for file in combined_pngs_dir.iterdir():
        gene, residue = get_gene_residue_from_filename(file.name)
        genes.add(gene)
    return genes


def create_list_of_files_for_ffmpeg(list_of_images_for_video, combined_pngs_dir, pauses, framerate):
    genes = get_set_of_genes_to_draw(combined_pngs_dir)
    with open(list_of_images_for_video, "w") as list_of_images_for_video_fh:
        for gene in genes:
            for residue in range(1, 1000000):
                image = combined_pngs_dir / f"gene_{gene}_residue_{residue}.png"
                if image.exists():
                    gene_residue = f"{gene}[{residue}]"
                    if gene_residue in pauses:
                        upper_bound = pauses[gene_residue]*framerate
                    else:
                        upper_bound = 1
                    for i in range(upper_bound):
                        print(f"file '{str(image)}'", file=list_of_images_for_video_fh)
                else:
                    break


def main():
    args = get_args()
    path_1 = Path(args.gisaid_dir)
    path_2 = Path(args.viridian_dir)
    output_dir = Path(args.output_dir)
    pauses = get_pauses(args.pause_file)
    framerate = args.framerate

    logging.info("Formatting original pngs...")
    output_dir.mkdir(parents=True)
    combined_pngs_dir = output_dir / "pngs"
    combined_pngs_dir.mkdir()
    for file_1 in path_1.iterdir():
        filename = file_1.name
        file_2 = path_2 / filename
        png_1 = Image.open(str(file_1))
        png_2 = Image.open(str(file_2))
        concatenated_image = concatenate_horizontally(png_1, png_2)
        labelled_image = add_label(concatenated_image, filename,
                                   top_padding=80, tree_title_1="gisaid", tree_title_2="viridian")
        labelled_image.save(combined_pngs_dir/filename)
    logging.info("Formatting original pngs - done!")

    logging.info("Creating video...")
    list_of_images_for_video = "list_images.txt"
    create_list_of_files_for_ffmpeg(list_of_images_for_video, combined_pngs_dir, pauses, framerate)
    (
        ffmpeg
        .input(list_of_images_for_video, r=framerate, f='concat', safe='0')
        .output(str(output_dir / "final.mp4"))
        .run(overwrite_output=True)
    )
    logging.info("Creating video - done!")


main()
