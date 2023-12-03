"""
Dataclasses for handling metadata
Author: M.G. Garcia
"""

import os
import uuid
import pandas as pd
import json
import warnings
from dataclasses import dataclass, field, asdict
from typing import Optional, List
from pymods import MODSReader

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

    def full_path(self) -> str:
        """Returns the full path of the file path

        Returns
        -------
        str
            full path of the file path
        """
        return str(os.path.join(self.root_path, self.file_path))

    def __str__(self) -> str:
        return os.path.join(self.root_path, self.file_path)


@dataclass
class Person:
    """
    Represents a person and its role
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
    Represents a (PDF) document
    """
    
    location: FilePath = field(init=True, default=None)

    def update_root_path(self, path: str) -> None:
        """Updates the root of the path of the document"""
        self.location.update_root_path(path)


@dataclass
class Visual:
    """A class for handling metadata of visuals (images)
    extracted from PDF files"""

    document: Document  # document where the visual is located
    document_page: int  # page number in the document index
    bbox: List[int]  # bounding box of the visual in the document page
    bbox_units: str  # units of the bounding box
    id: Optional[str] = field(init=False)  # unique identifier
    # caption of the visual
    caption: Optional[list] = field(init=False, default=None)
    # one of: photo, drawing, map, etc.
    visual_type: Optional[str] = field(init=False, default=None)
    # location where the visual is stored
    location: FilePath = field(init=False, default=None)

    def __post_init__(self):
        self.id = str(uuid.uuid4())

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
            self.caption = [caption]
        elif len(self.caption) < 2:
            self.caption.append(caption)
        else:
            raise Warning(f"Maximum number of captions already set. Ignoring \
                          caption: {self.caption}")

    def set_location(self, location: FilePath, update: bool = False) -> None:
        """Sets the location where the visual is stored

        Parameters
        ----------
        location: FilePath
            location where the visual is stored
        update: bool
            if True, the root_path of location will be updated. If False,
            an error will be raised if the location is already set

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
    Represents the collection of metadata of an entry.
    An entry consits of a MODS file and zero or mor PDF files.
    Most of the fields are based on the MODS standard.
    """

    documents: List[Document] = field(init=False, default=None)

    persons: List[Person] = field(init=False, default=None)
    faculty: Faculty = field(init=False, default=None)
    mods_file: str = field(init=False, default=None)  # location of the MODS file

    title: str = field(init=False, default=None)
    abstract: str = field(init=False, default=None)
    submission_date: str = field(init=False, default=None)  # year, month, day
    thesis_type: str = field(init=False, default=None)  # master or bachelor thesis
    # list of subjects defined in repository
    subjects: List = field(init=False, default=None)
    copyright: str = field(init=False, default=None)
    languages: List[dict] = field(init=False, default=None)  # list of languages
    uuid: Optional[str] = field(init=False, default=None)  # unique identifier
    # identifiers: List = field(init=False) #
    iid: str = field(init=False, default=None)  # internal identifier
    media_type: List = field(init=False, default=None)  # internet media type
    issuance: List = field(init=False, default=None)  # type of issuance
    digital_origin: str = field(init=False, default=None)  # digital origin
    doi: str = field(init=False, default=None)  # digital object identifier
    edition: str = field(init=False, default=None)  # edition
    extent: List = field(init=False, default=None)  # extent
    form: List = field(init=False, default=None)  # form
    classification: List = field(init=False, default=None)  # classification
    collection: str = field(init=False, default=None)  # collection
    geo_code: List = field(init=False, default=None)  # geographic code
    corp_names: List = field(init=False, default=None)  # corporate names
    creators: List = field(init=False, default=None)  # creators
    physical_description: List = field(init=False, default=None)  # physical description
    physical_location: List = field(init=False, default=None)  # physical location
    pid: str = field(init=False, default=None)  # persistent identifier
    publication_place: List = field(init=False, default=None)  # publication place
    publisher: List = field(init=False, default=None)  # publisher
    purl: List = field(init=False, default=None)  # persistent URL
    type_resource: str = field(init=False, default=None)  # type of resource
    # URL at Educational Repository
    web_url: str = field(init=False, default=None)
    # total number of images/visuals extracted from the PDF files for
    # this entry in the repository
    total_visuals: Optional[int] = field(init=False, default=0)
    visuals: Optional[List[Visual]] = field(init=False, default=None)

    #  pdf_location: Optional[str] = field(init=False, default=None) # location of the PDF file

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

        Raises
        ------
        TypeError
            if document is not a Document object

        """

        if not isinstance(document, Document):
            raise TypeError('document must be a Document object')

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
            raise ValueError('PDF location already set. User overwrite=True to\
                             overwrite it.')
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

        if self.web_url and overwrite is False:
            raise ValueError('base URL already set. User overwrite=True to\
                             overwrite it.')
        else:
            if self.uuid is not None:
                if self.uuid[:5] == 'uuid:':  # some uuids start with uuid:
                    self.web_url = f'{base_url}{self.uuid}'
                else:  # pure uuids do not start with uuid:
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

        Raises
        ------
        TypeError
            if visual is not a Visual object

        """

        if not isinstance(visual, Visual):
            raise TypeError('visual must be a Visual object')
        
        if not self.visuals:
            self.visuals = []
        self.visuals.append(visual)

        # update total number of visuals
        self.total_visuals += 1

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


def main() -> None:
    pass
   
    
if __name__ == "__main__":
    main()
