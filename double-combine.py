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
    pdfWriter = PyPDF2.PdfWriter()
    # Hack to get around PyPDF2 bug - need to keep files open
    input_files = []
    for in_file in sys.argv[1:]:
        logger.info("Adding: %s", in_file)
        in_pdf_file = open(in_file, "rb")
        input_files.append(in_pdf_file)
        inpdf = PyPDF2.PdfReader(in_pdf_file)
        logger.info("\t %d pages", len(inpdf.pages))
        pdfWriter.append_pages_from_reader(inpdf)
        pdfWriter.add_bookmark(in_file, len(pdfWriter.pages) - len(inpdf.pages))
        if len(inpdf.pages) % 2 != 0:
            pdfWriter.add_blank_page()
    out_file = "combined-%d-files.pdf" % len(input_files)
    with open(out_file, "wb") as outFileObj:
        logger.info(
            "Writing %s, %d total pages", out_file, len(pdfWriter.pages)
        )
        pdfWriter.write(outFileObj)
    for inf in input_files:
        inf.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Given a list of PDF files, combine them into a single document ensuring that each doc will start on a new page if printed double-sided."
    )
    combine()
