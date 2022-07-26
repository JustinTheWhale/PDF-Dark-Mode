# JustinTheWhale

"""
Program that converts all of the .pdf files
in the same directory to have a "Dark mode"
to put less strain on your eyes :-)
Final file will be saved with the same name
but with "_darkmode.pdf" at the end


Things to note:
Might take a while depending on how large your .pdf(s) is/are
The final file is much larger than the original file
"""

import multiprocessing as mp
import os
import sys
from threading import Thread

import cv2
import numpy as np
from fpdf import FPDF
from numba import jit, uint8
from pdf2image import convert_from_path
from PIL import Image
from PyPDF2 import PdfFileMerger


class Darkmode:
    """
    Attributes
    ----------
    threads : int
        An integer representing the available cpu threads. More than 16
        caused strange issues on Windows.
    pdfs : list[str]
        A list of string(s) of pdf files to process.
    pngs : list[str]
        A list of string(s) of png files to process.
    temp_pdfs : list[str]
        A list of string(s) of temp_pdf files to process.
    pdf_groups : dict{str : [str]}
        A dict conatining the base filename for a pdf and a list of its 
        converted pages.
    batches : list[list]
        A list of lists to distribute the processing evenly on the CPU.

    Methods
    -------
    pdf_to_png(dpi_count=300):
        Iterates through each pdf file in self.pdfs and separates indiviual
        pages into separate png files. The names of the png files are saved
        in self.pngs.

    make_batches(task_list):
        Makes a list of lists where len(list) does not exceed cpu count. If
        a large PDF is encountered, each page will be converted by its own
        process. Starting more processes than cpu count might lead to 
        performance regression.
    
    make_processes():
        Adds process objects to self.process_list.

    start_processes():
        Starts indiviual process objects in self.process_list.

    make_threads():
        Adds thread objects to self.thread_list.

    start_threads():
        Starts indiviual thread objects in self.thread_list.

    def speed(image):
        Uses numba to quickly parse image array and change pixels to grey.

    black_to_grey(file):
        Takes inverted .png image and converts all black pixels to grey.

    png_to_pdf(png):
        Converts darkmode .png files to .pdf files. Adds temp filename to
        self.temp_pdfs after.

    get_groups():
        Goes through temp pdf files to group PDF pages by filename.
        Changes value of self.pdfs.
    
    repack(self):
        Packs all converted pdf files into a single PDF. Uses self.temp_pdfs
        for processing.
    """

    def __init__(self, pdfs=None):
        self.threads = mp.cpu_count()
        if self.threads > 16:
            self.threads = 16
        self.pdfs = []
        self.pngs = []
        self.temp_pdfs = []
        self.pdf_groups = {}
        self.process_list = []
        self.thread_list = []
        self.batches = []

    def pdf_to_png(self, dpi_count=300):
        """
        Iterates through each pdf file in self.pdfs and separates indiviual
        pages into separate png files. The names of the png files are saved
        in self.pngs.

        Arguments:
            dpi_count (Optional)) : int that specifies dpi when processing.
            Higher dpi scales with longer processing and higher quality.
        """

        for file in self.pdfs:
            pages = convert_from_path(
                file, dpi=dpi_count, thread_count=self.threads, grayscale=True
            )
            new_name = file[:-4]

            for page in pages:
                name = f"{new_name}-page{str(pages.index(page)).zfill(4)}.png"
                self.pngs.append(name)
                page.save(name, "PNG", compress_level=1)
                inverted = np.where(cv2.imread(name) <= 140, 255, 0)
                cv2.imwrite(name, inverted)

    def make_batches(self, task_list):
        """
        Makes a list of lists where len(list) does not exceed cpu count. If
        a large PDF is encountered, each page will be converted by its own
        process. Starting more processes than cpu count might lead to 
        performance regression. 

        Arguments:
            task_list (list): List of threads/processes.
            cpus (int): How long each sublist will be.

        Returns:
            batches (list) : List of lists where each sub-list is <= cpus.

        """

        if len(task_list) <= self.threads:
            return [task_list]
        else:
            batches = [
                task_list[i : i + self.threads]
                for i in range(len(task_list), self.threads)
            ]
            return batches

    def make_processes(self):
        """
        Adds process objects to self.process_list.
        """
        for file in self.pngs:
            p = mp.Process(target=self.black_to_grey, args=(file,))
            self.process_list.append(p)

    def start_processes(self):
        """
        Starts indiviual process objects in self.process_list.
        """
        self.process_list = self.make_batches(self.process_list)
        for i in range(len(self.process_list)):
            for p in self.process_list[i]:
                p.start()
            for p in self.process_list[i]:
                p.join()

    def make_threads(self):
        """
        Adds thread objects to self.thread_list.
        """
        for file in self.pngs:
            t = Thread(target=self.png_to_pdf, args=(file,))
            self.thread_list.append(t)

    def start_threads(self):
        """
        Starts indiviual thread objects in self.thread_list.
        """

        self.thread_list = self.make_batches(self.thread_list)
        for i in range(len(self.thread_list)):
            for t in self.thread_list[i]:
                t.start()
            for t in self.thread_list[i]:
                t.join()

    @staticmethod
    @jit(nopython=True, cache=True, fastmath={"fast"})
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

    def black_to_grey(self, file):
        """
        Takes inverted .png image and converts all black pixels to grey.

        Arguments:
            file (str) : String representing string filename.

        """

        color_array = cv2.imread(file)
        color_array = self.speed(color_array)
        cv2.imwrite(file, color_array)

    def png_to_pdf(self, png):
        """
        Converts darkmode .png files to .pdf files. Adds temp filename to
        self.temp_pdfs after.

        Arguments:
            png (str): String representing string filename.

        """

        pdf = FPDF()
        pdf.add_page()
        pdf.image(png, 0, 0, 210, 300)
        name = png.replace(".png", "_temp_darkmode.pdf")
        pdf.output(name, "F")
        pdf.close()
        self.temp_pdfs.append(name)
        os.remove(png)

    def get_groups(self):
        """
        Goes through temp pdf files to group PDF pages by filename.
        Changes value of self.pdfs.

        """

        pdfs = {}
        for file in sorted(self.temp_pdfs):
            if file.endswith(".pdf") and "darkmode" in file:

                pdf_file = file.split("-")[0]
                if pdf_file in pdfs:
                    pdfs[pdf_file].append(file)

                else:
                    pdfs[pdf_file] = [file]
        self.temp_pdfs = pdfs

    def repack(self):
        """
        Packs all converted pdf files into a single PDF. Uses self.temp_pdfs
        for processing.

        """

        pdfs = list(self.temp_pdfs.keys())

        for pdf in pdfs:
            merger = PdfFileMerger()

            for file in self.temp_pdfs[pdf]:
                merger.append(file)
            name = f"{pdf}_converted.pdf"
            merger.write(name)
            merger.close()


def main(files=None):
    """
    Main function, creates object and calls class methods.

    Arguments:
        files (Optional) : str or list of files to convert.

    """
    darkmode_generator = Darkmode()
    if files is not None:
        if isinstance(files, list) and files != []:
            for file in files:
                if not os.path.exists(file):
                    print(f"Can't find {file} with the given path, exiting!")
                    return
                else:
                    darkmode_generator.pdfs.append(file)

        elif isinstance(files, str):
            if os.path.exists(files):
                darkmode_generator.pdfs = [files]
            else:
                print(f"Can't find {files} with the given path, exiting!")
                return
        else:
            print("Invalid file type detected, exiting!")
            return
    else:
        # This does all
        darkmode_generator.pdfs = []
        for file in os.listdir("."):
            if file.endswith(".pdf") and "_converted" not in file:
                darkmode_generator.pdfs.append(file)

    darkmode_generator.pdf_to_png()
    darkmode_generator.make_processes()
    darkmode_generator.start_processes()
    darkmode_generator.make_threads()
    darkmode_generator.start_threads()
    darkmode_generator.pdf_groups = darkmode_generator.get_groups()
    darkmode_generator.repack()
    for item in darkmode_generator.temp_pdfs.values():
        for i in item:
            os.remove(i)


def convert(files=None):
    """
    Calls the main function, This is what should be called when using package.

    Arguments:
        files (Optional) : str or list of files to convert.
    """
    main(files=files)


if __name__ == "__main__":
    n = len(sys.argv)
    if n == 1:
        convert()
    elif n == 2:
        if "pdf" in sys.argv[1]:
            convert(files=sys.argv[1])
    else:
        files = sys.argv
        files.pop(0)
        for i in range(len(files)):
            if "pdf" in files[i]:
                pass
            else:
                files.pop(i)
        if files != []:
            convert(files=files)