# JustinTheWhale

'''
Program that converts all of the .pdf files
in the same directory to have a "Dark mode"
to put less strain on your eyes :-)
Final file will be saved with the same name
but with "_darkmode.pdf" at the end


Things to note:
Might take a while depending on how large your .pdf(s) is/are
Only one function uses multiprocessing but other fuctions might 
be added later
The final file is much larger than the original file
'''

import multiprocessing as mp
import os
from threading import Thread

import cv2
import numpy as np
from fpdf import FPDF
from numba import jit, uint8
from pdf2image import convert_from_path
from PIL import Image
from PyPDF2 import PdfFileMerger


def pdf_to_png(threads, dpi_count=300):
    """
    Uses pdf2image to grab individual pages out of pdf file.

    Arguments:
        threads (int) : How many threads to pass to convert_from_path().
        dpi_count (int) : (Optional) Dpi count for extraction, default is 300
    """

    for file in os.listdir("."):
        if file.endswith(".pdf") and not file.endswith('_converted.pdf'):
            pages = convert_from_path(file, dpi=dpi_count, 
                                      thread_count=threads, grayscale=True)
            new_name = file[:-4]

            for page in pages:
                name = f'{new_name}-page{str(pages.index(page)).zfill(4)}.png'
                page.save(name, 'PNG', compress_level=1)
                inverted = np.where(cv2.imread(name) <= 140, 255, 0)
                cv2.imwrite(name, inverted)


@jit(nopython=True, cache=True, fastmath={'fast'})
def speed(image):
    """
    Uses numba to quickly parse image array and change pixels to grey.

    Arguments:
        image (numpy.array) : Image in contained within a numpy array.
    
    Returns:
        image (numpy.array) : Converted numpy.image array

    """

    grey = np.full((3), fill_value=70, dtype=np.uint8)
    for i in range(len(image)):
        for j in range(len(image[0])):
            if np.sum(image[i, j]) == 0:
                image[i, j] = grey
    return image


def black_to_grey(file):
    """
    Takes inverted .png image and converts all black pixels to grey.

    Arguments:
        file (str) : String representing string filename.

    """

    color_array = cv2.imread(file)
    color_array = speed(color_array)
    cv2.imwrite(file, color_array)


def remove_temp_pdfs():
    """
    Removes PDF's in current directory.

    """

    for file in os.listdir("."):
        if "temp_darkmode.pdf" in file:
            os.remove(file)


def remove_pngs():
    """
    Removes PNG's in current directory.

    """

    for file in os.listdir("."):
        if file.endswith(".png"):
            os.remove(file)


def get_groups():
    """
    Goes through directory to group PDF pages by filename.

    Returns:
        pdfs (dict): dict of strings containing list of filename strings.
    
    """

    pdfs = {}
    for file in sorted(os.listdir('.')):
        if file.endswith('.pdf') and 'darkmode' in file:
            
            pdf_file = file.split('-')[0]
            if pdf_file in pdfs:
                pdfs[pdf_file].append(file)

            else:
                pdfs[pdf_file] = [file]
    return pdfs
    
    
def repack(pdf_files):
    """
    Packs all converted pdf files into a single PDF.

    Arguments:
        pdf_files (dict): dict of strings containing list of filename strings.
    
    """

    pdfs = list(pdf_files.keys())

    for pdf in pdfs:
        merger = PdfFileMerger()

        for file in pdf_files[pdf]:
            merger.append(file)
        name = f"{pdf}_converted.pdf"
        merger.write(name)
        merger.close()
    

def png_to_pdf(png):
    """
    Converts darkmode .png files to .pdf files.

    Arguments:
        png (str): String representing string filename.
    
    """

    pdf = FPDF()
    pdf.add_page()
    pdf.image(png, 0, 0, 210, 300)
    name = png.replace('.png', '_temp_darkmode.pdf')
    pdf.output(name, "F")
    pdf.close()
    

def make_batches(task_list, cpus):
    """
    Makes a list of lists where len(list) does not exceed cpu count.

    Arguments:
        task_list (list): List of threads/processes.
        cpus (int): How long each sublist will be.
    
    Returns:
        batches (list) : List of lists where each sub-list is <= cpus.

    """
    if len(task_list) <= cpus:
        return [task_list]
    else:
        batches = [task_list[i:i + cpus] for i in range(len(task_list), cpus)]
        return batches


def convert():
    """
    Main function, uses above functions to convert PDF files. Uses 
    multiprocessing/threading for speedup.

    """

    count = mp.cpu_count()
    if count > 16:
        count = 16

    pdf_to_png(count) # Grabs pngs from pdf

    # multiprocessing for conversion from black -> grey
    p_list = []
    for file in os.listdir("."):
        if file.endswith(".png"):
            p = mp.Process(target=black_to_grey, args=(file, ))
            p_list.append(p)

    batch = make_batches(p_list, count)

    for i in range(len(batch)):
        for p in batch[i]:
            p.start()
        for p in batch[i]:
            p.join()

    # multithreading for saving each image as a PDF 
    t_list = []
    for file in os.listdir("."):
        if file.endswith(".png"):
            t = Thread(target=png_to_pdf, args=(file, ))
            t_list.append(t)

    batch = make_batches(t_list, count)

    for i in range(len(batch)):
        for t in batch[i]:
            t.start()
        for t in batch[i]:
            t.join()

    remove_pngs()
    # List of files in order to repack into a single PDF
    files = get_groups()
    repack(files) 
    remove_temp_pdfs()


if __name__ == "__main__":
    convert()
