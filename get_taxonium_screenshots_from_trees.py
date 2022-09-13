small_test = True

import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import gzip
import json
from collections import defaultdict
from PIL import Image
import logging
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)


def get_locus_to_mutation(json_filepath):
    """
    Return a locus_to_mutation dict, with key (gene, residue_pos) and value (previous_residue, new_residue)
    Note: if gene is "nt" then the residue is a nucleotide instead of aminoacid
    """
    with gzip.open(json_filepath) as tree_fh:
        mutations_description = next(tree_fh).strip()
    mutations = json.loads(mutations_description)
    mutations = mutations["mutations"]

    locus_to_mutation = {}
    for mutation in mutations:
        locus = (mutation["gene"], mutation["residue_pos"])
        mutation_description = (mutation["previous_residue"], mutation["new_residue"])

        locus_to_mutation[locus] = mutation_description

    return locus_to_mutation


def get_chrome():
    logging.info("Getting chrome...")
    chrome_options = Options()
    chrome_options.headless = True
    chrome_options.add_argument('--user-data-dir=user_data')
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome("./chromedriver", options=chrome_options)
    return driver


def get_screenshot_from_taxonium(jsonl_file: Path, screenshot_dir: Path, gene_to_highest_position, right_x, lower_y):
    screenshot_dir.mkdir(parents=True, exist_ok=False)

    driver = get_chrome()
    driver.get("https://taxonium.org/")
    time.sleep(1)
    upload_element = driver.find_element(By.XPATH, "//input[@class='text-sm mb-3']")
    upload_element.send_keys(str(jsonl_file.resolve()))

    colour_by_element = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[3]/div[2]/div/div[2]/div[1]/select"))
    )
    time.sleep(10)  # TODO: improve this

    colour_by_element = Select(colour_by_element)
    colour_by_element.select_by_visible_text("Genotype")

    residue_position = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[3]/div[2]/div/div[2]/div[2]/label[2]/input")

    for gene in gene_to_highest_position.keys():
        gene_elem = Select(driver.find_element(By.XPATH, "/html/body/div[1]/div/div[3]/div[2]/div/div[2]/div[2]/label[1]/select"))
        gene_elem.select_by_value(gene)
        time.sleep(5)

        for position in range(1, gene_to_highest_position[gene]+1):
            logging.info(f"Getting image for gene {gene} residue {position}")
            residue_position.clear()
            residue_position.send_keys(str(position))
            main_view_elem = driver.find_element(By.ID, "view-main")
            tmp_image_path = screenshot_dir/f"gene_{gene}_residue_{position}_tmp.png"
            image_path = screenshot_dir/f"gene_{gene}_residue_{position}.png"
            main_view_elem.screenshot(str(tmp_image_path))
            image = Image.open(str(tmp_image_path))
            cropped_image = image.crop((362, 251, right_x, lower_y))
            cropped_image.save(str(image_path))
            tmp_image_path.unlink()
            time.sleep(0.1)


def get_gene_to_highest_position(mutations_list):
    gene_to_highest_position = defaultdict(int)
    for mutations in mutations_list:
        for (gene, position) in mutations.keys():
            gene_to_highest_position[gene] = max(gene_to_highest_position[gene], position)
    return gene_to_highest_position


def main():
    logging.info("Getting highest position for each gene...")
    mutations_gisaid = get_locus_to_mutation("gisaid_illumina.opt.taxonium.jsonl.gz")
    mutations_viridian = get_locus_to_mutation("viridian_illumina.opt.taxonium.jsonl.gz")
    gene_to_highest_position = get_gene_to_highest_position([mutations_gisaid, mutations_viridian])
    if small_test:
        gene_to_highest_position = {"ORF1b": 20}

    logging.info("Getting highest position for each gene - done!")
    logging.info(f"gene_to_highest_position = {gene_to_highest_position}")

    logging.info("Getting screenshots for gisaid...")
    get_screenshot_from_taxonium(jsonl_file=Path("gisaid_illumina.opt.taxonium.jsonl.gz"),
                                 screenshot_dir=Path("vis_gisaid"),
                                 gene_to_highest_position=gene_to_highest_position,
                                 right_x=497, lower_y=908)
    logging.info("Getting screenshots for gisaid - done!")

    logging.info("Getting screenshots for viridian...")
    get_screenshot_from_taxonium(jsonl_file=Path("viridian_illumina.opt.taxonium.jsonl.gz"),
                                 screenshot_dir=Path("vis_viridian"),
                                 gene_to_highest_position=gene_to_highest_position,
                                 right_x=464, lower_y=937)
    logging.info("Getting screenshots for viridian - done!")


main()
