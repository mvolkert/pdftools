import os
from typing import List

import fpdf
import PyPDF2
from natsort import natsorted
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg

__all__ = ["interlace", "interlace_per_dir", "merge", "merge_per_dir", "write_images", "merge_svgs_per_dir"]


def interlace(front_name: str, back_name: str, out_name: str):
    pdf_front = open(front_name, 'rb')
    pdf_back = open(back_name, 'rb')
    reader_front = PyPDF2.PdfReader(pdf_front)
    reader_back = PyPDF2.PdfReader(pdf_back)
    writer = PyPDF2.PdfWriter()

    num_pages = len(reader_front.pages)
    if not num_pages == len(reader_back.pages):
        return

    for i in range(0, num_pages):
        print(i, num_pages, num_pages - i)
        writer.add_page(reader_front.pages[i])
        writer.add_page(reader_back.pages[num_pages - 1 - i])

    with open(out_name, "wb") as pdf_out:
        writer.write(pdf_out)

    pdf_front.close()
    pdf_back.close()


def interlace_per_dir(in_dir: str, out_dir: str):
    for (dirpath, dirnames, filenames) in os.walk(in_dir):
        for front_name, back_name in list(_group(filenames, 2)):
            out_name = os.path.join(out_dir, front_name + "_interlaced.pdf")
            front_name = os.path.join(in_dir, front_name)
            back_name = os.path.join(in_dir, back_name)
            interlace(front_name, back_name, out_name)


def merge2(filenames: List[str], output: str):
    merger = PyPDF2.PdfMerger()
    pdfs = []

    for filename in filenames:
        pdf = open(filename, 'rb')
        merger.append(pdf)

    with open(output, 'wb') as pdf_out:
        merger.write(pdf_out)

    for pdf in pdfs:
        pdf.close()


def merge(filenames: List[str], output: str):
    writer = PyPDF2.PdfWriter()
    pdfs = []

    for filename in filenames:
        pdf = open(filename, 'rb')
        reader = PyPDF2.PdfReader(pdf)

        for i in range(0, len(reader.pages)):
            writer.add_page(reader.pages[i])

        pdfs.append(pdf)

    with open(output, "wb") as pdf_out:
        writer.write(pdf_out)

    for pdf in pdfs:
        pdf.close()

def merge_many_pages(filename: str, output: str, page_multiplier: int):
    writer = PyPDF2.PdfWriter()

    pdf = open(filename, 'rb')
    reader = PyPDF2.PdfReader(pdf)

    for j in range(0, page_multiplier):
        for i in range(0, len(reader.pages)):
            writer.add_page(reader.pages[i])


    with open(output, "wb") as pdf_out:
        writer.write(pdf_out)

    pdf.close()


def merge_per_dir(in_dir: str, out_dir: str):
    counter = 0

    for (dirpath, dirnames, filenames) in os.walk(in_dir):
        out_name = os.path.join(out_dir, "merged_%03d.pdf" % counter)
        filenames = [os.path.join(dirpath, filename) for filename in filenames]
        merge(filenames, out_name)
        counter += 1


def write_images(images: List[str], output: str):
    pdf = fpdf.FPDF()

    for image in images:
        pdf.add_page()
        pdf.image(image)
    pdf.output(output + ".pdf", "F")


def _group(lst, n):
    """group([0,3,4,10,2,3], 2) => [(0,3), (4,10), (2,3)]

    Group a list into consecutive n-tuples. Incomplete tuples are
    discarded e.g.

    group(range(10), 3)
    [(0, 1, 2), (3, 4, 5), (6, 7, 8)]
    """
    return zip(*[lst[i::n] for i in range(n)])


def merge_svgs_per_dir(in_dir="", out_dir=""):
    if not in_dir:
        in_dir = os.getcwd()

    if not out_dir:
        out_dir = os.getcwd()

    for (dirpath, dirnames, filenames) in os.walk(in_dir):
        basename = os.path.basename(dirpath)
        if basename.startswith("."):
            continue
        out_name = os.path.join(out_dir, basename + ".pdf")
        filenames = [os.path.join(dirpath, filename) for filename in filenames if ".svg" in filename]
        filenames = natsorted(filenames)
        if len(filenames) == 0:
            continue
        pdf_filenames = [convert_svg(filename) for filename in filenames]
        print(pdf_filenames)
        merge(pdf_filenames, out_name)


def convert_svg(filename: str) -> str:
    drawing = svg2rlg(filename)
    pdf_name = filename.replace(".svg", ".pdf")
    renderPDF.drawToFile(drawing, pdf_name)
    return pdf_name
    

def replace_last_page(filename: str, lastpage: str, offset: int = 0):
    '''
    offset: if last page is not at the end
    '''
    pdf_front = open(filename, 'rb')
    pdf_back = open(lastpage, 'rb')
    reader_front = PyPDF2.PdfReader(pdf_front)
    reader_back = PyPDF2.PdfReader(pdf_back)
    writer = PyPDF2.PdfWriter()

    num_pages = len(reader_front.pages)

    for i in range(0, num_pages - 1 - offset):
        print(i, num_pages, num_pages - i)
        writer.add_page(reader_front.pages[i])
    writer.add_page(reader_back.pages[0])
    for i in range(num_pages - offset, num_pages):
        print(i, num_pages, num_pages - i)
        writer.add_page(reader_front.pages[i])

    with open(filename.replace(".pdf", "_merged.pdf"), "wb") as pdf_out:
        writer.write(pdf_out)

    pdf_front.close()
    pdf_back.close()
