"""
Python script. Given a list of PDF files, combine them into a single document,
ensuring that each doc will start on a new page if the whole thing is printed
double-sided.

Requires PyPDF2

:copyright: (c) 2018 by Phil Siino Haack.
:license: Apache2, see LICENSE for more details.
"""

import argparse
import logging
import sys


import PyPDF2


def combine():
    logger = logging.getLogger("double-combine")
    pdfWriter = PyPDF2.PdfFileWriter()
    # Hack to get around PyPDF2 bug - need to keep files open
    input_files = []
    for in_file in sys.argv[1:]:
        logger.info("Adding: %s", in_file)
        in_pdf_file = open(in_file, "rb")
        input_files.append(in_pdf_file)
        inpdf = PyPDF2.PdfFileReader(in_pdf_file)
        logger.info("\t %d pages", inpdf.numPages)
        pdfWriter.appendPagesFromReader(inpdf)
        pdfWriter.addBookmark(in_file, pdfWriter.getNumPages() - inpdf.numPages)
        if inpdf.numPages % 2 != 0:
            pdfWriter.addBlankPage()
    out_file = "combined-%d-files.pdf" % len(input_files)
    with open(out_file, "wb") as outFileObj:
        logger.info("Writing %s, %d total pages", out_file, pdfWriter.getNumPages())
        pdfWriter.write(outFileObj)
    for inf in input_files:
        inf.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Given a list of PDF files, combine them into a single document ensuring that each doc will start on a new page if printed double-sided."
    )
    combine()
