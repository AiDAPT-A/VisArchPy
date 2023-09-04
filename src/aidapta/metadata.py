"""
Dataclasses for handling metadata for extracted visuals
Author: M.G. Garcia
"""

import os
import uuid
import pandas as pd
import json
from dataclasses import dataclass, field, asdict
from typing import Optional, List


@dataclass
class Person:
    """
    Represents a person 
    """
    name: str
    role: str


@dataclass
class Department:
    """
    Represents a department in a Faculty
    """
    name: str


@dataclass
class Faculty:
    """
    Represents a Faculty
    """
    name: str
    departments: List[Department]


@dataclass
class Document:
    """
    Represents a document
    """
    location: str # location where the document is stored


@dataclass
class FilePath:
    """
    Represents a file path
    """
    root_path: str
    file_path: str

    def __post_init__(self):
        if not isinstance(self.root_path, str):
            raise TypeError("root_path must be a string")
        if not isinstance(self.file_path, str):
            raise TypeError("file_path must be a string")

    def update_root_path(self, root_path: str) -> None:
        """Updates the root path of the file path
        
        Parameters
        ----------
        root_path: str
            new root path
        
        Returns
        -------
        None
        """
        self.root_path = root_path
    
    def __str__(self) -> str:
        return os.path.join(self.root_path, self.file_path)


@dataclass
class Visual:
    """A class for handling metadata for architectural visuals
    extracted from PDF files"""

   
    document: Document # document where the visual is located
    document_page: int # page number in the document index
    bbox: List[int] # bounding box of the visual in the document page
    bbox_units: str # units of the bounding box
    id : Optional[str] = field(init=True, default=str(uuid.uuid4())) # unique identifier
    caption: Optional[list] = field(init=False, default=None) # caption of the visual    
    visual_type: Optional[str] = field(init=False, default=None) # one of: photo, drawing, map, etc
    location: FilePath = field(init=False, default=None) # location where the visual is stored

    def set_visual_type(self, visual_type: str) -> None:
        """Sets the visual type. One of photo, drawing, map, etc.
        
        Parameters
        ----------
        visual_type: str
            type of visual
        
        Returns
        -------
        None
        """
        self.visual_type = visual_type

    def set_caption(self, caption: str) -> None:
        """Sets the caption for the visual
        
        Parameters
        ----------
        caption: str
            caption for the visual
        
        Returns
        -------
        None

        Raises
        ------
        Warning
            If the caption already contains two elements

        """

        if self.caption is None: 
            self.caption = [ caption ]
        elif len(self.caption) < 2:
            self.caption.append(caption)
        else:
            raise Warning(f"Maximum number of captions already set. Ignoring caption: {self.caption}")
        
    def set_location(self, location: FilePath, update: bool = False) -> None:
        """Sets the location where the visual is stored
        
        Parameters
        ----------
        location: FilePath
            location where the visual is stored
        update: bool
            if True, the root_path of location will be updated. If False, an error will be raised
        
        Returns
        -------
        None

        Raises
        ------
        ValueError
            If the location is already set and update is False
        """

        if self.location and not update:
            raise ValueError("Location already set.")
        elif self.location and update:
            self.location.update_root_path(location.root_path)
        else:
            self.location = location


@dataclass
class Metadata:
    """
    Represents metadata of an entry in the library repository
    """

    documents: List[Document] = field(init=False, default=None)

    persons: List[Person] = field(init=False, default=None)
    faculty: Faculty = field(init=False, default=None)
    mods_file: str = field(init=False) # location of the MODS file

    title: str = field(init=False)
    abstract: str = field(init=False)
    submission_date: str = field(init=False) # year, month, day
    thesis_type: str = field(init=False) # master or bachelor thesis
    subjects: List = field(init=False) # list of subjects defined in repository
    copyright: str = field(init=False) 
    languages: List[dict] = field(init=False) # list of languages
    uuid: Optional[str] = field(init=False, default=None)  # unique identifier
    # identifiers: List = field(init=False) #
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
    purl: List = field(init=False) # persistent URL
    type_resource: str = field(init=False) # type of resource
    web_url: str = field(init=False, default=None) # URL at Educational Repository
    
    visuals: Optional[List[Visual]] = field(init=False, default=None)
    # pdf_location: Optional[str] = field(init=False, default=None) # location of the PDF file

    def set_metadata(self, metadata: dict) -> None:
        """ Sets metadata for a repository entry 
        
        Parameters
        ----------
        metadata: dict
            dictionary with metadata from MODS file
        
        Returns
        -------
        None
        
        """
        
        self.persons = metadata.get('persons')
        self.faculty = metadata.get('faculty')
        self.mods_file = metadata.get('modsfile')

        self.title = metadata.get('title')
        self.abstract = metadata.get('abstract')
        self.submission_date = metadata.get('date')
        self.thesis_type = metadata.get('genre') 
        self.subjects = metadata.get('subjects')
        self.copyright = metadata.get('rights') 
        self.languages = metadata.get('language')

        self.uuid = metadata.get('identifiers')
        self.iid = metadata.get('iid')
        self.media_type = metadata.get('internet_media_type')
        self.issuance = metadata.get('issuance')
        self.digital_origin = metadata.get('digital_origin')
        self.doi = metadata.get('doi')
        self.edition = metadata.get('edition')
        self.extent = metadata.get('extent')
        self.form = metadata.get('form')
        self.classification = metadata.get('classification')
        self.collection = metadata.get('collection')
        self.geo_code = metadata.get('geo_code')
        self.corp_names = metadata.get('corp_names')
        self.creators = metadata.get('creators')
        self.physical_description = metadata.get('physical_description')
        self.physical_location = metadata.get('physical_location')
        self.pid = metadata.get('pid')
        self.publication_place = metadata.get('publication_place')
        self.publisher = metadata.get('publisher')
        self.purl = metadata.get('purl')
        self.type_resource = metadata.get('type_resource')

    def add_document(self, document: Document) -> None:
        """ Adds a document object to the metadata 
        
        Parameters
        ----------
        document: Document
            document object
        
        Returns
        -------
        None

        """
        if not self.documents:
            self.documents = []
        self.documents.append(document)
    
    def add_pdf_location(self, path_pdf: str, overwrite: bool = False) -> None:
        """ Sets location of the PDF file 
        
        Parameters
        ----------
        path_pdf: str
            path to the PDF file
        overwrite: bool
            if True, overwrites the PDF location if it is already set
        
        Returns
        -------
        None
        
        Raises
        ------
        ValueError
            if PDF location is already set and overwrite is False
        """

        if self.pdf_location and overwrite:
            raise ValueError('PDF location already set. User overwrite=True to overwrite it.')
        else:
            self.pdf_location = path_pdf

    def add_web_url(self, base_url: str, overwrite: bool = False) -> None:
        """ Adds a URL to the metadata 
        
        Parameters
        ----------  
        base_url: str
            base URL of the repository
        overwrite: bool
            if True, overwrites the web URL if it is already set           
        
        Returns
        -------
        None

        Raises
        ------
        ValueError
            if web URL is already set and overwrite is False
        
        """

        if self.web_url and overwrite == False:
            raise ValueError('base URL already set. User overwrite=True to overwrite it.')
        else:
            if self.uuid[:5] == 'uuid:': # some uuids start with uuid:
                self.web_url = f'{base_url}{self.uuid}' 
            else: # pure uuids do not start with uuid:
                self.web_url = f'{base_url}uuid:{self.uuid}'
    
    def add_visual(self, visual: Visual) -> None:
        """ Adds a visual to the metadata 
        
        Parameters
        ----------
        visual: Visual
            visual object
        
        Returns
        -------
        None
        
        """
        if not self.visuals:
            self.visuals = []
        self.visuals.append(visual)

    def as_dict(self) -> dict:
        """ Returns metadata as a dictionary """
        return asdict(self)
    
    def as_dataframe(self) -> pd.DataFrame:
        """ Returns metadata as a Pandas DataFrame """
        return pd.DataFrame([self.as_dict()])
    
    def save_to_csv(self, filename: str) -> None:
        """ Writes metadata to a CSV file 
        
        Parameters
        ----------
        filename: str
            name of the CSV file

        Returns
        -------
        None
        
        """

        self.as_dataframe().to_csv(filename, index=False)
    
    def save_to_json(self, filename: str) -> None:
        """ Writes metadata to a JSON file 
        
        Parameters
        ----------
        filename: str
            name of the JSON file
        
        Returns
        -------
        None
        """

        with open(filename, 'w') as f:
            json.dump(self.as_dict(), f, indent=4)
    

def main() -> None:
    from aidapta.utils import extract_mods_metadata

    meta_blob = extract_mods_metadata('data-pipelines/data/00001.mods.xml')
    
    person1 = Person(name='John Doe', role='author')
    person2 = Person(name='Jane Doe', role='mentor')

    department1 = Department(name='Department of Architecture')

    faculty1 = Faculty(name='Faculty of Architecture', departments=[department1])

    document1 = Document(location='data-pipelines/data/4563050_AmberLuesink_P5Report_TheRevivaloftheJustCity.pdf')

    meta_data = Metadata(documents=[document1])
    meta_data.set_metadata(meta_blob)

    print(meta_data.as_dict())
    # meta_data.write_to_csv('data-pipelines/data/metadata.csv')

    # print(meta_data.as_dataframe())
    
if __name__ == "__main__":
    main()
