import requests
import re
import os
import pathlib
from bs4 import BeautifulSoup


def create_output_dir(base_path: str, path="") -> str:
    """
    creates a directory in the base path if it doesn't exists.

    Parameters
    ----------
    base_path: str
        path to destination directory
    name: str
        name or path for the new directory, parent directories are
        created if they don't exists

    Returns
    -------
    Pathlib object
        relative path (comibining base_path and path) to the
        newly created directory
    """

    if isinstance(base_path, pathlib.Path):
        base_path = str(base_path)

    full_path = os.path.join(base_path, path)
    pathlib.Path(full_path).mkdir(parents=True, exist_ok=True)

    return pathlib.Path(full_path)


def convert_mm_to_point(quantity: float) -> float:
    """
    Converts a quantity in milimeters to points (1/72 inches)

    Parameters
    ----------
    quantity: float
        quantity in milimeters

    Returns
    -------
    float
        quantity in points
    """

    return quantity * 2.8346456693


def convert_dpi_to_point(quantity: float, dpi: int) -> float:
    """
    Converts a quantity in dots per inch (dpi) to points (1/72 inches)

    Parameters
    ----------
    quantity: float
        quantity in dots per inch

    Returns
    -------
    float
        quantity in points
    """

    if not isinstance(dpi, int):
        raise TypeError("dpi must be an integer")
    if dpi < 0:
        raise ValueError("dpi must be positive")

    return quantity / dpi * 72


def extract_metadata_from_html(reference_url: str) -> dict:
    """ Extracts metadata from HTML pages from the Thesis repository,
    TU Delft Library.

    Parameters
    ----------
    reference_url: str
        URL from 'to reference to this document use'

    Returns
    -------
    dict
        metadata from HTML page
    """

    # download html page
    html_doc = requests.get(reference_url)
    html_doc.raise_for_status

    # parsing html content
    soup = BeautifulSoup(html_doc.content, 'html.parser')
    pdf_object = soup.find_all("fieldset",
                               class_="islandora islandora-metadata")
    meta_element, val_element = pdf_object[0].find_all("span", class_="label"),
    pdf_object[0].find_all("span", class_="value")

    attributes_ = []
    for attribute in meta_element:
        attributes_.append(attribute.text.lower())  # attribute names are
        # converted to lower case
    # TODO: find a way to separate subject keyworkds

    values_ = []
    for val in val_element:
        if val.text == "Subject":
            print("this is the subject")
        values_.append(val.find("p").text)

    # assamble result in a dictionary
    metadata = {attributes_[i]: values_[i] for i in range(len(attributes_))}

    return metadata


def download_PDF(download_url: str, destination: str) -> None:
    """
    Downloads files from the Thesis repository, TU Delft Library to
    a destination directory

    Parameters
    ----------
    download_url: str
        URL of the file to download
    destination: str
        path to a directory to store the downloaded file

    Returns
    -------
    None
    """

    response = requests.get(download_url, stream=True)
    # get file name
    dis = response.headers['content-disposition']
    file_name = re.findall("filename=(.+)", dis)[0]

    # remove double quoates from file name
    new_file_name = file_name.strip('"')

    # prepare output directory, it will be created if it
    # doesn't exists
    full_path = create_output_dir(destination)
    file_path = os.path.join(full_path, new_file_name)

    # stream file content and save it to destination
    with open(file_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=2000):
            f.write(chunk)

    return None


def get_entry_number_from_mods(mods_file_path: str) -> str:
    """
    Extracts the entry number from a MODS file name.
    It assumes the number is the first 5 characteris of the file name.
    This function is specific to the Delft dataset.

    Parameters
    ----------
    mods_file_path: str
        path to a MODS file

    Returns
    -------
    str
        the number of an entry with leading zeros
    """

    return mods_file_path.split("/")[-1][:5]


if __name__ == '__main__':

    pass
