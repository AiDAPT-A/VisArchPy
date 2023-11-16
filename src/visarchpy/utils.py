import requests
import re
import os
import pathlib
import warnings
from pymods import MODSReader
from bs4 import BeautifulSoup
from visarchpy.metadata import Person, Faculty, Department


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


def extract_mods_metadata(mods_file: str) -> dict:
    """ Extract metadata from MODS files, version 3.6

    Parameters
    ----------
    mods_file: str
        path to MODS file

    Returns
    -------
    dict
        Dictionary with MODS elements and values
    """

    mods = MODSReader(mods_file)

    meta = {}
    meta["modsfile"] = mods_file

    for record in mods:

        # Thesis Title
        meta["title"] = record.titles[0]

        # Abtracts
        abstracts = []  # MODS allows multiple abstract
        [abstracts.append(abstract.text) for abstract in record.abstract]
        meta["abstract"] = abstracts

        # Dates
        dates = []  # MODS allows multiple dates
        [dates.append(date.text) for date in record.dates]
        meta["date"] = dates[0]
        if len(dates) > 1:
            raise ValueError("More than one date found in MODS file")

        # Type of work, MSC or bachelor thesis
        genre = []  # MODS allows multiple abstract
        [genre.append(g.text) for g in record.genre]
        meta["genre"] = genre

        # Departments
        departments = []  # MODS allows multiple departments
        [departments.append(Department(name=department.text)) for department
         in record.get_notes(type='department')]
        meta["department"] = departments

        # Faculty
        faculties = []  # MODS allows multiple faculties
        [faculties.append(Faculty(name=faculty.text, departments=departments))
         for faculty in record.get_notes(type='faculty')]
        meta["faculty"] = faculties

        # subjects
        subjects = []  # MODS allows multiple subjects (keywords)
        [subjects.append(subject.text) for subject in record.subjects]
        meta["subjects"] = subjects

        # Author and Mentor names as <surname>, <initials>
        persons = []
        # dictionary with fullname and role
        [persons.append(Person(name=name.text, role=name.role.text)) for
         name in record.names]
        meta["persons"] = persons

        # Copyright statement
        rights = []  # MODS allows multiple copyright statements
        [rights.append(right.text) for right in record.rights]
        if len(rights) > 1:
            raise ValueError("More than one copyright found in MODS file")
        else:
            meta["rights"] = rights

        # Language
        languages = []  # MODS allows multiple languages
        [languages.append(
            {"code": language.code, "authority": language.authority}
            ) for language in record.language]
        meta["language"] = languages

        # Identifiers
        if record.identifiers:  # some MODS files don't have identifiers
            meta["identifiers"] = record.identifiers[0].text  # MODS allows
            # multiple identifiers
        else:
            warnings.warn("No identifiers found in MODS file")
        # only the first one is used. Uuid is used as identifier
        meta["iid"] = record.iid
        meta["internet_media_type"] = record.internet_media_type
        meta["issuance"] = record.issuance
        meta["digital_origin"] = record.digital_origin
        meta["doi"] = record.doi
        meta["edition"] = record.edition
        meta["extent"] = record.extent
        meta["form"] = record.form
        meta["classification"] = record.classification
        meta["collection"] = record.collection
        meta["geographic_code"] = record.geographic_code

        corp_names = []  # MODS allows multiple corporate names
        # we collect the name and the role of each corporate name
        [corp_names.append(
            {"name": corp_name.text, "role": corp_name.role.text}
            ) for corp_name in record.get_corp_names]
        meta["corp_names"] = corp_names

        meta["rights"] = rights

        meta["creators"] = record.get_creators
        meta["physical_description"] = record.physical_description_note
        meta["physical_location"] = record.physical_location
        meta["pid"] = record.pid
        meta["publication_place"] = record.publication_place
        meta["publisher"] = record.publisher
        meta["purl"] = record.purl
        meta["type_resource"] = record.type_of_resource

    return meta


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
    mods_file = "/home/manuel/Documents/devel/VisArchPy/tests/data/sample-mods.xml"
    meta = extract_mods_metadata(mods_file)
    print(meta)
    # pass
