# Py CTakes Parser
Python utilities to parse the output of cTAKES 4.0.

Repository is a port of the Julia repository found here - https://github.com/bcbi/CTakesParser.jl

# Installation
## From PyPi

```python
pip install ctakes_parser
```

## From Github Master

```python
pip install git+https://github.com/titu1994/PyCTakesParser.git
```

# Examples

## Parse Single File

```python
from ctakes_parser import ctakes_parser as parser

df = parser.parse_file(file_path='notes_in/mts_sample_note_97_1152.txt.xmi')
```

## Parse Entire Directory

```python
from ctakes_parser import ctakes_parser as parser

parser.parse_dir(in_directory_path='notes_in/',
                 out_directory_path='notes_out/')
```
