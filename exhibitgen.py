"""
Simple module for generating legal exhibit pages slipsheets.

The slipsheets are letter-sized portrait or landscape single page PDFs with a
horizontally and vertically centered exhibit designation i.e. "Exhibit A"

:copyright: (c) 2020 by Phil Siino Haack.
:license: Apache2, see LICENSE for more details.
"""
import argparse
import os.path
import re
import shutil
import string
import tempfile

import PyPDF2
import reportlab.lib.pagesizes
import reportlab.platypus
import reportlab.lib.styles
import reportlab.lib.units

TITLE = "Exhibit %s"

STYLES = reportlab.lib.styles.getSampleStyleSheet()

#######################
# UTILITY FUNCTIONS
#######################
_CLEANLIST = []


def exhibit_with_cleanup(fn, label):
    global _CLEANLIST
    filename = fn(label)
    _CLEANLIST.append(filename)
    return filename


def cleanup():
    global _CLEANLIST
    for f in _CLEANLIST:
        if os.path.exists(f):
            os.remove(f)
    _CLEANLIST = []


A_UPPERCASE = ord("A")
ALPHABET_SIZE = 26


def _decompose(number):
    """Generate digits from `number` in base alphabet, least significants
    bits first.

    Since A is 1 rather than 0 in base alphabet, we are dealing with
    `number - 1` at each iteration to be able to extract the proper digits.
    """
    while number:
        number, remainder = divmod(number - 1, ALPHABET_SIZE)
        yield remainder


def base_alphabet_to_10(ltr_label):
    """Convert an alphabet "number" to its decimal representation"""
    return sum(
        (ord(letter) - A_UPPERCASE + 1) * ALPHABET_SIZE ** i
        for i, letter in enumerate(reversed(ltr_label.upper()))
    )


def base_10_to_alphabet(number):
    """Convert a decimal number to its base alphabet representation"""
    return "".join(chr(A_UPPERCASE + part) for part in _decompose(number))[::-1]


def _next_label(label):
    """
    Given a label like "A" or 1 (i.e. mixed types are ok), return the next
    label in the sequence.
    """
    try:
        return int(label) + 1
    except ValueError:
        # Assume a string
        out = base_10_to_alphabet(base_alphabet_to_10(label) + 1)
        if label.islower():
            return out.lower()
        return out


def _valid_label(input) -> bool:
    if input not in string.ascii_letters:
        try:
            int(input)
        except ValueError:
            return False
    return True


label_re = re.compile(r"([a-zA-Z])\W|(\d+)")


def label_from_filename(filename: str) -> str:
    """
    Attempt to guess a proposed exhibit number/letter from a filename.

    Valid formats include any form of:
        [Exhibit string][optional space or underline][valid label]*.pdf
        or
        [valid label]*.pdf
    where:
        [Exhibit string] is one of:
            "Exhibit"
            "Ex.", Ex ", "Ex_"
            "Exh.", "Exh ", "Exh_"

    """
    if filename[:8].lower() in ["exhibit.", "exhibit_", "exhibit "]:
        remainder = filename[8:]
    elif filename[:7].lower() == "exhibit":
        remainder = filename[7:]
    elif filename[:4] in ["Exh.", "Exh ", "Exh_"]:
        remainder = filename[4:]
    elif filename[:3].lower() in ["ex.", "ex ", "ex_"]:
        remainder = filename[3:]
    else:
        # maybe the label is at the beginning
        remainder = filename
    print(f"REM: {remainder}")
    result = label_re.match(remainder.strip())
    if result:
        return result.group(1) if result.group(1) else result.group(2)
    raise ValueError(f"No valid label name found for input file: {filename}")


def exhibit_page(canvas, doc, font_face="Times-Bold", font_size=72):
    """
    This is a callback function that creates the exhibit page with the parameters set
    by generate_exhibit()
    """
    canvas.saveState()
    # canvas.setPageSize(doc.pagesize)
    canvas.setFont(font_face, font_size)
    canvas.drawCentredString(doc.pagesize[0] / 2.0, doc.pagesize[1] / 2.0, doc.title)
    canvas.restoreState()


def portrait_exhibit(label):
    """
    Wrapper around generate_exhibit() that specifies portrait orientation
    """
    return generate_exhibit(
        f"Exhibit_{label}.pdf",
        f"Exhibit {label}",
        pagesize=reportlab.lib.pagesizes.letter,
    )


def landscape_exhibit(label):
    """Wrapper around generateExhibit() that specifies landscape orientation"""
    return generate_exhibit(
        f"Exhibit_{label}.pdf",
        f"Exhibit {label}",
        pagesize=reportlab.lib.pagesizes.landscape(reportlab.lib.pagesizes.letter),
    )


def generate_exhibit(filename, designation, pagesize, page_callback=exhibit_page):
    """
    Generate an exhibit at path "filename" with the exhibit text specified
    by "designation."  The PDF title will be set to the same string.  The
    "pagesize" parameter expects a tuple in points (1/72 in.).  Useful defaults
    are found in reportlab.lib.pagesizes.
    """
    inch = reportlab.lib.units.inch
    doc = reportlab.platypus.SimpleDocTemplate(
        filename, title=designation, pagesize=pagesize, leftMargin=(0.8 * inch)
    )
    story = [reportlab.platypus.Spacer(1, 2 * inch)]
    doc.build(story, onFirstPage=page_callback)
    return filename


def add_slipsheet(infile, outfile, label, exh_fn):
    # Write to a temp file in case something goes wrong
    # conveniently also handles when infile == outfile
    tempdir = tempfile.mkdtemp()
    out = os.path.join(tempdir, "temp.pdf")
    pdfWriter = PyPDF2.PdfFileWriter()
    print(
        f"Adding exhibit slipsheet '{label}' to file: '{infile}'',"
        f" writing to {outfile}"
    )
    with open(out, "wb") as out_f:
        exh_file = exhibit_with_cleanup(exh_fn, label)
        ep = PyPDF2.PdfFileReader(exh_file)
        pdfWriter.appendPagesFromReader(ep)
        content = PyPDF2.PdfFileReader(infile)
        pdfWriter.appendPagesFromReader(content)
        pdfWriter.write(out_f)
    try:
        shutil.move(out, outfile)
    finally:
        # shutil.rmtree(tempdir)
        pass
    cleanup()


def is_portrait(pdf_filename):
    pdf_reader = PyPDF2.PdfFileReader(pdf_filename)
    deg = pdf_reader.getPage(0).get("/Rotate")
    page = pdf_reader.getPage(0).mediaBox
    if (
        page.getUpperRight_x() - page.getUpperLeft_x()
        > page.getUpperRight_y() - page.getLowerRight_y()
    ):
        if deg in [0, 180, None]:
            return False
        return True
    else:
        if deg in [0, 180, None]:
            return True
        else:
            return False


def main():
    """
    Tool for generating and handling legal exhibits in PDF format.
    It can add a slipsheet to a PDF or generate a series of slipsheets
    for manual addition starting with an arbitrary letter or number.
    """
    #######################
    # Argument parsing
    #######################
    description = """
    Tool for generating and handling legal exhibits in PDF format. 
    It can add a slipsheet to a PDF or generate a series of slipsheets 
    for manual addition starting with an arbitrary letter or number.
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "-c",
        "--count",
        type=int,
        help='Number of exhibits to generate.  Ignored unless FILE is "NONE".',
        default=1,
    )
    parser.add_argument(
        "-o",
        "--orientation",
        choices=["landscape", "portrait"],
        help="Page orientation (default: based on first page of FILE)",
    )
    parser.add_argument(
        "-l",
        "--label",
        type=str,
        help='Number or letter to use as the initial label (e.g. "A" or "1". '
        "By default, exhibitgen will pull from the input filename.",
    )
    parser.add_argument(
        "infile",
        nargs="+",
        help="Path to one or more PDFs to which an exhibit slipsheet should be added. "
        'Use "NONE" to create slipsheets.',
    )
    args = parser.parse_args()
    print(args)

    label = args.label
    if label and not _valid_label(label):
        parser.error(
            f"Invalid label '{label}'. Valid labels are ASCII letters and integers."
        )

    if args.infile[0].lower() == "none":
        if args.orientation == "landscape":
            exhibit_fn = landscape_exhibit
        else:
            exhibit_fn = portrait_exhibit  # default to portrait
        for _ in range(args.count):
            exhibit_fn(label)
            label = _next_label(label)

    else:
        use_label = label
        for inf in args.infile:
            exhibit_fn = None
            if args.orientation == "landscape":
                exhibit_fn = landscape_exhibit
            elif args.orientation == "portrait":
                exhibit_fn = portrait_exhibit
            else:
                if is_portrait(inf):
                    exhibit_fn = portrait_exhibit
                else:
                    exhibit_fn = landscape_exhibit
            base = os.path.basename(inf)
            if not label:
                use_label = label_from_filename(base)
                outfile = inf
            else:
                outfile = f"Ex_{use_label}_{base}"
            add_slipsheet(inf, outfile, use_label, exhibit_fn)
            use_label = _next_label(use_label)


if __name__ == "__main__":
    main()
