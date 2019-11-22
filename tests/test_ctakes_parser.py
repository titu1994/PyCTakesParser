import os
import pandas as pd
import pytest

from ctakes_parser import ctakes_parser as parser


def assert_dataframe(df):
    assert len(df) == 157
    assert len(df[df['scheme'] == 'SNOMEDCT_US']) == 149
    assert len(df[df['scheme'] == 'RXNORM']) == 8
    assert len(df[df['refsem'] == 'UmlsConcept']) == 157


def test_output_df():
    df = parser.parse_file(file_path='notes_in/mts_sample_note_97_1152.txt.xmi')

    assert_dataframe(df)


def test_parse_directory():
    in_dir = 'notes_in/'
    out_dir = 'notes_out/'

    parser.parse_dir(in_dir, out_dir)

    assert os.path.exists(os.path.join(out_dir, 'mts_sample_note_97_1152.txt.csv'))
    assert os.path.exists(os.path.join(out_dir, 'mts_sample_note_97_1152_2.txt.csv'))
    assert os.path.exists(os.path.join(out_dir, 'test_no_preferred_text.csv'))

    df1 = pd.read_csv(os.path.join(out_dir, 'mts_sample_note_97_1152.txt.csv'), header=0, index_col=None)
    df2 = pd.read_csv(os.path.join(out_dir, 'mts_sample_note_97_1152_2.txt.csv'), header=0, index_col=None)
    df3 = pd.read_csv(os.path.join(out_dir, 'test_no_preferred_text.csv'), header=0, index_col=None)

    assert_dataframe(df1)
    assert_dataframe(df2)
    assert_dataframe(df3)


if __name__ == '__main__':
    pytest.main(__file__)
