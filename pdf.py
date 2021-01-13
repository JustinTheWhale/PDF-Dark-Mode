#JustinMartinezCSUSB


#pdfdarkmode_noGUI.py


#Program that converts all of the .pdf files
#in the same directory to have a "Dark mode"
#to put less strain on your eyes :-)
#Final file will be saved with the same name
#but with "_darkmode.pdf" at the end


#Things to note:
#Might take a while depending on how large your .pdf(s) is/are
#Only one function uses multiprocessing but other fuctions might 
#be added later
#The final file is much larger than the original file, but this
#is to keep the quality intact.


from pdf2image import convert_from_path
from PyPDF2 import PdfFileMerger
import multiprocessing as mp
from threading import Thread
from fpdf import FPDF
import cv2
import os
import time
from compare import speed
import timeit
from alive_progress import alive_bar, config_handler





#Function that converts the individual pages in a .pdf file 
#to .png for easier pixel value manipulation. Returns a list of
#.png files. ##############UPDATE

def pdf_to_png(dpi_count, threads):
    jpg_names = []
    for File in os.listdir("."):
        if File.endswith(".pdf"):
            pages = convert_from_path(File, dpi=dpi_count, thread_count=threads, use_pdftocairo=True, fmt='jpeg', jpegopt={'quality':50, 'progressive' : False, 'optimize': True})
            new_name = File[:-4]
            with alive_bar(total=len(pages), calibrate=1, title='Extracting images from PDF') as bar:
                for page in pages:
                    name = '%s-page%d.jpg' % (new_name, pages.index(page))
                    page.save(name, 'JPEG')
                    inverted = cv2.bitwise_not(cv2.imread(name))
                    cv2.imwrite(name, inverted)
                    bar()
                        

#Takes an inverted .png and converts all black pixels to grey.
#Only takes one string at a time so that multiprocessing works.
def black_to_grey(File):
    color_array = cv2.imread(File)
    start = time.time()
    color_array = speed(color_array)
    print("Finished", File, "in", time.time() - start, "seconds")
    cv2.imwrite(File, color_array)
 

#Returns a sorted list of darkmode .png files
def darkmode_files():
    file_list = []
    for File in os.listdir("."):
        if "_darkmode" in File:
            file_list.append(File)
    return sorted(file_list)


#Returns a list of index's for the get_groups(arg) function
def get_start_end(darkmode_list, element):
    index_list = []
    tuple_list = []
    for i in enumerate(darkmode_list):
        tuple_list.append(i)
    for j in range(len(tuple_list)):
        if element in tuple_list[j][1]:
            index_list.append(tuple_list[j][0])
    return index_list


#Returns a list of grouped .png files. This so we dont
#confuse the pages of two sparate .pdf files
def get_groups (darkmode_list):
    group_list = []
    i = 0
    while i < len(darkmode_list):
        start_end_list = get_start_end(darkmode_list, darkmode_list[i][:-24])
        start = start_end_list[0]
        end = start_end_list[len(start_end_list)-1]
        i = end + 1
        items = tuple(darkmode_list[start:i])
        group_list.append(items)
    return group_list


#Simple cleanup
def remove_temp_pdfs():
    for File in os.listdir("."):
        if "temp_darkmode.pdf" in File:
            os.remove(File)


#Simple cleanup
def remove_pngs():
    for File in os.listdir("."):
        if File.endswith(".jpg"):
            os.remove(File)


#Takes a list of darkmode .pdf pages and merges them into
#a single .pdf file.
def repack(darkmode_pdfs):
    for i in range(len(darkmode_pdfs)):
        merger = PdfFileMerger()        
        for j in range(len(darkmode_pdfs[i])):
            merger.append(darkmode_pdfs[i][j])
        merger.write(darkmode_pdfs[i][j][:-24] + "_darkmode.pdf")
        merger.close()


#Converts darkmode .png files to .pdf files
def png_to_pdf(jpg):
    pdf = FPDF()
    pdf.add_page()
    pdf.image(jpg, 0, 0, 210, 300)
    pdf.output(jpg[:-4] + "_temp_darkmode.pdf", "F")
    pdf.close()


#Simply making a list of lists to process for multiprocessing.
#Size of the lists is determined by the number of cpus. This is so
#that we dont more processes than cpus available. 
def make_batches(process_list, cpus):
    batches = [process_list[i:i + cpus] for i in range(0, len(process_list), cpus)]
    return batches


# Calls almost all of the funtions above and uses different Processes
# for black_t0_grey(File) which results in a significant speedup over
# only 1 process. The speedup is based on a cpu-cores/pages-to-process
# ratio since it converts in batches.
def multiProcess(cpus):
    pdf_to_png(500, cpus)
    p_list = []
    for File in os.listdir("."):
        if File.endswith(".jpg"):
            p = mp.Process(target=black_to_grey, args=(File, ))
            p_list.append(p)
    batch = make_batches(p_list, cpus)
    for i in range(len(batch)):
        print("Batch ", i, " starting now with length", len(batch[i]))
        for p in batch[i]:
            p.start()
        for p in batch[i]:
            p.join()
    t_list = []
    for File in os.listdir("."):
        if File.endswith(".jpg"):
            t = Thread(target=png_to_pdf, args=(File, ))
            t_list.append(t)
    batch = make_batches(t_list, cpus)
    for i in range(len(batch)):
        print("Batch ", i, " starting now with length", len(batch[i]))
        for t in batch[i]:
            t.start()
        for t in batch[i]:
            t.join()
    remove_pngs()
    repack(get_groups(darkmode_files())) # Repacks back into PDF's
    remove_temp_pdfs()

if __name__ == "__main__":
    '''
    for File in os.listdir("."):
        if File.endswith(".jpg"):
            os.remove(File)
    config_handler.set_global(bar='smooth', spinner='brackets')
    '''
    start = time.time()
    multiProcess(mp.cpu_count())
    print(time.time() - start)
