"""
Python port of the Julia package to parse CTakes outputs into Pandas Dataframes

Original source code - https://github.com/bcbi/CTakesParser.jl
"""
import os
import glob
import pandas as pd
from lxml import etree

from ctakes_parser import helpers


def _safe_cast(cast, val):
    if val is not None:
        val = cast(val)
    return val


def parse_dir(directory_path, out_directory_path):
    if not os.path.exists(directory_path):
        raise FileNotFoundError("Directory not found at {}!".format(directory_path))

    if not os.path.isdir(directory_path):
        raise NotADirectoryError("Provided path {} is not a directory !".format(directory_path))

    if not os.path.exists(out_directory_path):
        os.makedirs(out_directory_path)

    files = sorted(glob.glob(os.path.join(directory_path, "*")))
    num_files = len(files)

    print("Parsing {} files from directory {}".format(num_files, directory_path))
    print("-" * 100)
    print()

    for file_id, file_path in enumerate(files):
        print("Processing file {}/{} (Path = {})".format(file_id + 1, num_files, file_path))

        df = parse_file(file_path)

        head, filename = os.path.split(file_path)
        filename = os.path.splitext(filename)[0]  # get just the filename
        filename = filename + '.csv'
        filename = os.path.join(out_directory_path, filename)

        df.to_csv(filename, index=None, encoding='utf8')

    print("Finished processing all files !")


def parse_file(file_path) -> pd.DataFrame:
    tree = etree.parse(file_path)
    root = tree.getroot()

    results = helpers.ResultDataframeModule()
    positions = helpers.PositionDataframeModule()

    for i, child in enumerate(root):
        namespace_keys = {v for k, v in child.nsmap.items()}

        if 'http:///org/apache/ctakes/typesystem/type/textsem.ecore' in namespace_keys:
            if 'ontologyConceptArr' in child.keys():

                name = etree.QName(child.tag).localname
                polarity = _safe_cast(int, child.get('polarity', '0'))
                negated = (polarity <= 0)
                pos_start = _safe_cast(int, child.get('begin', None))
                pos_end = _safe_cast(int, child.get('end', None))

                confidence = _safe_cast(float, child.get('confidence', None))
                uncertainty = _safe_cast(float, child.get('uncertainty', None))
                conditional = _safe_cast(bool, child.get('conditional', None))
                generic = _safe_cast(bool, child.get('generic', None))
                subject = child.get('subject', None)

                oca = child.get("ontologyConceptArr").split(" ")
                for c in oca:
                    results.insert(textsem=name, id=int(c), pos_start=pos_start, pos_end=pos_end,
                                   negated=negated, confidence=confidence, uncertainty=uncertainty,
                                   conditional=conditional, generic=generic, subject=subject)

        if 'http:///org/apache/ctakes/typesystem/type/refsem.ecore' in namespace_keys:
            name = etree.QName(child.tag).localname

            scheme = child.get('codingScheme', None)
            cui = child.get('cui', None)
            preferred_text = child.get('preferredText', None)
            id = _safe_cast(int, child.get('{http://www.omg.org/XMI}id', None))
            tui = child.get('tui', None)
            score = _safe_cast(float, child.get('score', None))

            results.update_val_at(id, 'refsem', name)
            results.update_val_at(id, 'cui', cui)
            results.update_val_at(id, 'preferred_text', preferred_text)
            results.update_val_at(id, 'scheme', scheme)
            results.update_val_at(id, 'tui', tui)
            results.update_val_at(id, 'score', score)

        if 'http:///org/apache/ctakes/typesystem/type/syntax.ecore' in namespace_keys:
            name = etree.QName(child.tag).localname

            if name == 'ConllDependencyNode' and child.get('id', '0') != '0':
                postag = child.get('postag', None)
                pos_start = _safe_cast(int, child.get('begin', None))
                pos_end = _safe_cast(int, child.get('end', None))
                text = child.get('form', None)

                positions.insert(pos_start=pos_start, pos_end=pos_end, part_of_speech=postag, text=text)

    results = results.to_dataframe()
    positions = positions.to_dataframe()

    positions.set_index('pos_start', drop=False, inplace=True)
    positions.index.name = 'index'

    def _positional_search(df):
        pos_start = df['pos_start']
        pos_end = df['pos_end']

        pos_rows = positions[(pos_start <= positions.index) & (positions.index < pos_end)]
        pos_rows = pos_rows['text'].values
        pos_rows = ' '.join(pos_rows)

        return pos_rows

    results['true_text'] = results.apply(_positional_search, axis=1)

    pos_df_subset = positions[['part_of_speech', 'pos_start']]
    final_df = pd.merge(results, pos_df_subset, on='pos_start', how='left')

    return final_df
