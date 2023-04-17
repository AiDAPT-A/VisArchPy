import requests
import re
import os
from pymods import MODSReader
from bs4 import BeautifulSoup
from aidapta.image import create_output_dir

from aidapta.metadata import Person, Faculty, Department


def extract_mods_metadata(mods_file: str) -> dict:
    """ Extract metadata from MODS files, version 3.6
    
    Params
    ======
    mods_file: path to MODS file

    Returns
    =======
    Dictionary with MODS elements and values
    """
    
    mods = MODSReader(mods_file)

    meta = {}
    meta["modsfile"] = mods_file

    for record in mods:

        # Thesis Title
        meta["title"] = record.titles[0]

        # Abtracts
        abstracts = [] # MODS allows multiple abstract
        for abstract in record.abstract:
            abstracts.append(abstract.text)
        meta["abstract"] = abstracts

        # Dates
        dates = [] # MODS allows multiple dates
        for date in record.dates:
            dates.append(date.text)
        meta["date"] = dates[0]
        if len(dates) > 1:
            raise ValueError("More than one date found in MODS file")

        # Type of work, MSC or bachelor thesis
        genre = [] # MODS allows multiple abstract
        for g in record.genre:
            genre.append(g.text)
        meta["genre"] = genre

        # Departments
        departments =[] # MODS allows multiple departments
        for department in record.get_notes(type='department'):
            departments.append(Department(name=department.text))
        meta["department"] = departments

        # Faculty
        faculties =[] # MODS allows multiple faculties
        for faculty in record.get_notes(type='faculty'):
            faculties.append(Faculty(name=faculty.text, departments=departments))   
        meta["faculty"] = faculties

        # subjects
        subjects = [] # MODS allows multiple subjects (keywords)
        for subject in record.subjects:
            # print(subject.text)
            subjects.append(subject.text)
        meta["subjects"] = subjects

        # Author and Mentor names as <surname>, <initials>
        persons = [] 
        for name in record.names:
            # dictionary with fullname and role
            
            person = Person(name=name.text, role=name.role.text)
            persons.append(person)
        meta["persons"] = persons

        # Copyright statement
        rights =[] # MODS allows multiple copyright statements
        for right in record.rights:
            rights.append(right.text)
        meta["rights"] = rights
        if len(rights) > 1:
            raise ValueError("More than one right found in MODS file")

        # Language
        languages = [] # MODS allows multiple languages
        for language in record.language:
            l = {"code": language.code, "authority": language.authority}
            languages.append(l)
        meta["language"] = languages

        meta["identifiers"] = record.identifiers[0].text # MODS allows multiple identifiers, 
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
        meta["corp_names"] = record.get_corp_names
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
    """
    Extracts metadata from HTML pages from the Thesis repository, TU Delft Library.

    param:
        reference_url: URL from 'to reference to this document use'
    """

    # download html page
    html_doc = requests.get(reference_url)
    html_doc.raise_for_status

    # parsing html content
    soup = BeautifulSoup(html_doc.content, 'html.parser')
    pdf_object = soup.find_all("fieldset", class_="islandora islandora-metadata") 
    meta_element, val_element = pdf_object[0].find_all("span", class_="label"), pdf_object[0].find_all("span", class_="value")

    attributes_ =[]
    for attribute in meta_element:
        attributes_.append(attribute.text.lower()) # attribute names are 
        # converted to lower case
    # TODO: find a way to separate subject keyworkds 

    values_ =[]
    for val in val_element:
        if val.text == "Subject":
            print("this is the subject")
        values_.append(val.find("p").text)
    
    # assamble result in a dictionary
    metadata = { attributes_[i]: values_[i] for i in range(len(attributes_))}

    return metadata


def download_PDF(download_url: str, destination: str) -> None:
    """
    Downloads files from the Thesis repository, TU Delft Library to 
    a destination directory

    param:
        download_url: URL of the file to download
        destination: path to a directory to store the downloaded file 
    """

    response = requests.get(download_url, stream=True)
    # get file name 
    dis = response.headers['content-disposition']
    file_name = re.findall("filename=(.+)", dis)[0]

    # remove double quoates from file name
    new_file_name = file_name.strip('"')

    # prepare output directory, it will be created if it
    # doesn't exists
    full_path =create_output_dir(destination)
    file_path = os.path.join(full_path, new_file_name)   

    # stream file content and save it to destination
    with open(file_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=2000):
            f.write(chunk) 
    
    return None

def get_entry_number_from_mods(mods_file_path: str) -> str:
    """
    Extracts the entry number from a MODS file name. 
    The number is the firts 5 characteris of the file name.
    
    param:
    ------
        mods_file_path: path to a MODS file
    """

    return mods_file_path.split("/")[-1][:5]


if __name__ == '__main__':
    mods_file = "data-pipelines/data/actual-data/00001_mods.xml"
    meta = extract_mods_metadata(mods_file)
    print(meta)