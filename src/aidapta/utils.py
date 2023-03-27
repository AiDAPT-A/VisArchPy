from pymods import MODSReader, MODSRecord
mods = MODSReader("data-pipelines/data/4Manuel_MODS.xml")


def extract_mods_metadata(mods_file: str) -> dict:
    """ Extract metadata from MODS files, version 3.6
    
    Params
    ======
    mods_file: path to MODS file

    Returns
    =======
    Dictionary with MODS elements and values
    """
    meta = {}

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
        meta["dates"] = dates

        # Type of work, MSC or bachelor thesis
        genre = [] # MODS allows multiple abstract
        for g in record.genre:
            genre.append(g.text)
        meta["genre"] = genre

        # Faculty
        faculties =[] # MODS allows multiple faculties
        for faculty in record.get_notes(type='faculty'):
            faculties.append(faculty.text)
        meta["faculty"] = faculties

        # Departments
        departments =[] # MODS allows multiple departments
        for department in record.get_notes(type='department'):
            departments.append(department.text)
        meta["department"] = departments
        
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
            person ={"name": name.text, "role": name.role.text} 
            persons.append(person)
        meta["names"] = persons

        # Copyright statement
        rights =[] # MODS allows multiple copyright statements
        for right in record.rights:
            rights.append(right.text)
        meta["rights"] = rights

        # Language
        languages = [] # MODS allows multiple languages
        for language in record.language:
            l = {"code": language.code, "authority": language.authority}
            languages.append(l)
        meta["language"] = languages

        meta["identifiers"] = record.identifiers
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
        meta["pyblication_place"] = record.publication_place
        meta["publisher"] = record.publisher
        meta["purl"] = record.purl
        meta["type_resource"] = record.type_of_resource
    
    return meta