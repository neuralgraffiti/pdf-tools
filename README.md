# pdf-tools
Tools for manipulating PDF files, particularly for legal applications.

There are two programs here:
1. exhibitgen: a python program for generating slipsheets for legal exhibits.
  The slipsheets are letter-sized portrait or landscape single page PDFs with a
  horizontally and vertically centered exhibit designation i.e. "Exhibit A"
  
  There is a compiled Mac version of this here.  

2. double-combine: A command-line python script that will take a list of PDF files and combine them into a single document, ensuring that each document will start on a new page if the whole thing is printed double-sided.

## exhibitgen usage
### Command line
```
usage: exhibitgen.py [-h] [-c COUNT] [-o {landscape,portrait}] [-l LABEL]
                     infile [infile ...]

Tool for generating and handling legal exhibits in PDF format. It can add a
slipsheet to a PDF or generate a series of slipsheets for manual addition
starting with an arbitrary letter or number.

positional arguments:
  infile                Path to one or more PDFs to which an exhibit slipsheet
                        should be added. Use "NONE" to create slipsheets.

optional arguments:
  -h, --help            show this help message and exit
  -c COUNT, --count COUNT
                        Number of exhibits to generate. Ignored unless FILE is
                        "NONE".
  -o {landscape,portrait}, --orientation {landscape,portrait}
                        Page orientation (default: based on first page of
                        FILE)
  -l LABEL, --label LABEL
                        Number or letter to use as the initial label (e.g. "A"
                        or "1". By default, exhibitgen will pull from the
                        input filename.
```
### Mac app (py2app)
Drag-and-drop appropriately-named input files on the app to insert a slipsheet. The orientation is guessed based on the orientation of the first page.
[Download the app here](https://github.com/neuralgraffiti/pdf-tools/releases).
