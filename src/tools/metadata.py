"""
Dataclasses for managing metadata for architectural visuals
Author: M.G. Garcia
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Tuple

@dataclass
class PDFVisual:
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

    print(visual.__dict__)

if __name__ == "__main__":
    main()

# TODO: check how to parse HTML: https://realpython.com/beautiful-soup-web-scraper-python/