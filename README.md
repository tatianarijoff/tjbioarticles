# tjbioarticles
## Table of contents
 - [Introduction](#introduction)
 - [Installation](#installation)
 - [Tasks performed by tjbioarticles](#tasks-performed-by-tjbioarticles)
 - [Structure of the package](#structure-of-the-package)
 - [Installation code](#installation-code)


## Introduction
"tjbioarticles" is a Python code which use the Biopython library to extract Pubmed articles information.
The current version follow current pep8 recommendations.

The aim of the tjbioarticles is:
- to combine different number of keywords columns
- for each column to define different keyword group that can be used in the postprocessing analysis
- to extract the articles associated to the keywords (PubMed ID)
- to extract and save the XML of each PubMed article
- to save the most important XML information into a pandas dataframe 
- to save the article's title, authors and abstract in a pdf document (obtained from LaTeX)

It is also possible to plot some usefull information like the articles for keywords, articles for countries, 
and articles per years.
 
The Excel file generated from pandas dataframe contains additional columns, for the moment filled in manually
that can be used for a second articles analysis.


## Installation
```bash
pip install tjbioarticles
```
assuming that the package has been downloaded in the current folder.

## Tasks performed by tjbioarticles


## Structure of the package

```tjbioarticles``` has the structure used for standard python packages. It consists in a folder named after the package "tjbioarticles" (which is also the top level of the git repository) 
that contains the source code, the required code and information for the installation, documentation, unit tests and usage examples. In particular:
 - The **source code** is contained in a subfolder that also has the same name of the python package (tjbioarticles).
    -- plot_util has been made for basic plot tests, it is available for your needs but it does not pretend to be a complete plot interface, we suggest you will develop your own plot way ;) 
 - **Unit tests** is contained in the folder "tests" 
 - **Examples** illustrating the package usage are hosted in the folder "examples"
 - **License** information is contained in the file "LICENSE.txt"
 - you can run the code using the run_analysis.py code taking inspiration from the example directory
 - This **documentation** is contained in the file "README.md"
 - The **installation process** is defined by the files ["pyproject.toml"](#pyprojecttoml), ["MANIFEST.in"](#manifestin), and  ["setup.py"](#setuppy), which will be described in more detail in the following section.
 



