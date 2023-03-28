"""
Dataclasses for managing metadata for architectural visuals
Author: M.G. Garcia
"""

import requests
import re
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Tuple
from bs4 import BeautifulSoup
from .image import create_output_dir
from datetime import date




dataclass
class Person:
    """
    Represents a person 
    """
    name: str
    role: str


dataclass
class Department:
    """
    Represents a department in a Faculty
    """
    name: str


dataclass
class Faculty:
    """
    Represents a Faculty
    """
    name: str
    departments: List(Department)


dataclass
class RepositoryEntry:
    """
    Represents metadata of an entry in a repository
    """

    persons: List[Person]
    faculty: Faculty 

    title: str = field(init=False)
    abstract: str = field(init=False)
    submission_date: date # year, month, day
    thesis_type: str = field(init=False) # master or bachelor thesis
    subjects: List = field(init=False) # list of subjects defined in repository
    copyright: str = field(init=False) 
    languages: List[dict] = field(init=False) # list of languages
    uuid: Optional[str] = field(init=False)  # unique identifier
    identifiers: List = field(init=False) #
    iid: str = field(init=False) # internal identifier
    media_type: List = field(init=False) # internet media type
    issuance: List = field(init=False) # type of issuance
    digital_origin: str = field(init=False) # digital origin
    doi: str = field(init=False) # digital object identifier
    edition: str = field(init=False) # edition
    extent: List = field(init=False) # extent
    form: List = field(init=False) # form
    classification: List = field(init=False) # classification
    collection: str = field(init=False) # collection
    geo_code: List = field(init=False) # geographic code
    corp_names: List = field(init=False) # corporate names
    creators: List = field(init=False) # creators
    physical_description: List = field(init=False) # physical description
    physical_location: List = field(init=False) # physical location
    pid: str = field(init=False) # persistent identifier
    publication_place: List = field(init=False) # publication place
    publisher: List = field(init=False) # publisher
    purl: str = field(init=False) # persistent URL
    type_resource: str = field(init=False) # type of resource

    def set_metadata(metadata:dict, self) -> None:
        """ Sets metadata for a repository entry """
        
        self.title = metadata.get('title')
        self.abstract = metadata.get('abstract')
        self.submission_date = date.fromisoformat(metadata.get('date'))
        self.thesis_type = metadata.get('genre') 
        self.subjects = metadata.get('subjects')
        self.copyright = metadata.get('rights') 
        self.languages = metadata.get('language')
        uuid: str = field(init=False)  # unique identifier
        identifiers: List = field(init=False) #
        iid: str = field(init=False) # internal identifier
        media_type: List = field(init=False) # internet media type
        issuance: List = field(init=False) # type of issuance
        digital_origin: str = field(init=False) # digital origin
        doi: str = field(init=False) # digital object identifier
        edition: str = field(init=False) # edition
        extent: List = field(init=False) # extent
        form: List = field(init=False) # form
        classification: List = field(init=False) # classification
        collection: str = field(init=False) # collection
        geo_code: List = field(init=False) # geographic code
        corp_names: List = field(init=False) # corporate names
        creators: List = field(init=False) # creators
        physical_description: List = field(init=False) # physical description
        physical_location: List = field(init=False) # physical location
        pid: str = field(init=False) # persistent identifier
        publication_place: List = field(init=False) # publication place
        publisher: List = field(init=False) # publisher
        purl: str = field(init=False) # persistent URL
        type_resource: str = field(init=False) # type of resource




@dataclass
class Visual:
    """A class for handling metadata for architectural visuals
    extracted from PDF files"""

    document_title: str
    document_author: str
    document_date: str # when document was created
    document_page: str # page number in the document index
    document_contributors: List
    document_type: str # master or bachelor thesis
    
    institution: str # degree granting insitution
    program: str 
    coordinates: Optional[Tuple] # latitude and longitud
    collection: str # part of collection
    reference: str # URI to repository
    copyright: str # rights
    repository_date:  datetime # date reported by TU Delft repository
    subjects: List # list of subjects defined in repository

    visual_location: str = field(init=False) # path to file containing visual
    visual_caption: str = field(init=False)
    pdf_page: int = field(init=False) # page number in the PDF layout
    visual_type: str = field(init=False) # one of: photo, drawing, map, etc


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


def main() -> None:
    
    document_title= 'title'
    document_author= 'author'
    document_date= datetime.today() # when document was created
    document_page= '3' # page number in the document index
    document_contributors = ['contrib1', 'contrib2']
    document_type = 'master thesis'
    
    institution= 'tu delft' # degree granting insitution
    program='architecture'
    coordinates= (1,2)
    collection= 'collection' # part of collection
    reference= 'https://url/' # URI to repository
    copyright= 'me' # rights
    repository_date= datetime.today() # date reported by TU Delft repository
    subjects= ['sub1', 'sub2'] # list of subjects defined in repository

    # visual_location:= field(init=False) # path to file containing visual
    # visual_caption: Optional[str]
    # pdf_page: int = field(init=False) # page number in the PDF layout
    # visual_type: Optional[str] # one of: photo, drawing, map, etc

    visual = PDFVisual(document_title, document_author, document_date, document_page, document_contributors, document_type, institution, program, coordinates, 
    collection, reference, copyright, repository_date, subjects)

    file_url= "https://repository.tudelft.nl/islandora/object/uuid%3A4457ef73-5f7e-47cd-9013-f2a78eca76df/datastream/OBJ/download" 

    download_PDF( file_url, "data-pipelines/data/test-download")
    
if __name__ == "__main__":
    main()
