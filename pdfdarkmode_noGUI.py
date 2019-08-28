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
from fpdf import FPDF
import cv2
import os


#Function that converts the individual pages in a .pdf file 
#to .png for easier pixel value manipulation. Returns a list of
#.png files.
def pdf_to_png(dpi_arg=175, thread_arg=1):
    arg_dict = locals()
    dpi_count = arg_dict['dpi_arg'] #Grabbing values of the
    threads = arg_dict['thread_arg'] #args to pass to convert_from_path.
    png_names = []
    for File in os.listdir("."):
        if File.endswith(".pdf"):
            pages = convert_from_path(File, dpi=dpi_count, thread_count=threads) #thread_count max is the number of cpus.
            new_name = File[:-4]
            for page in pages:
                page.save('%s-page%d.png' % (new_name, pages.index(page)), 'PNG')
                png_names.append('%s-page%d.png' % (new_name, pages.index(page)))
    return png_names


#Takes the list of .png's and inverts the color for each.
#It's necessary because otherise black font wouldn't look right.
def invert_color(pngs_white):
    for i in range(len(pngs_white)):
        image = cv2.imread(pngs_white[i])
        image_inverted = cv2.bitwise_not(image)
        cv2.imwrite(pngs_white[i], image_inverted)
        

#Takes an inverted .png and converts all black pixels to grey.
#Only takes one string at a time so that multiprocessing works.
def black_to_grey(File):
    color_array = cv2.imread(File)
    length = (color_array.shape[0] - 1)
    width = (color_array.shape[1] - 1)
    for i in range(0, length):
        for j in range(0, width):
            if color_array[i, j].tolist() == [0, 0, 0]:
                color_array[i, j] = [100, 100, 100]
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
        if File.endswith(".png"):
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
def png_to_pdf(pngs_dark):
    for x in range(len(pngs_dark)):
        pdf = FPDF()
        pdf.add_page()
        pdf.image(pngs_dark[x], 0, 0, 210, 300)
        pdf.output(pngs_dark[x][:-4] + "_temp_darkmode.pdf", "F")
        pdf.close()
    remove_pngs()
    repack(get_groups(darkmode_files())) # Repacks back into PDF's
    remove_temp_pdfs()


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
# For example:
#               4-cores/4-pages = 1 core per page
def multiProcess(cpus):
    temp_pngs = pdf_to_png(thread_arg=mp.cpu_count())
    invert_color(temp_pngs)
    p_list = []
    for File in os.listdir("."):
        if File.endswith(".png"):
            p = mp.Process(target=black_to_grey, args=(File, ))
            p_list.append(p)
    batch = make_batches(p_list, cpus)
    for i in range(len(batch)):
        print("Batch ", i, " starting now with length", len(batch[i]))
        for p in batch[i]:
            p.start()
        for p in batch[i]:
            p.join()
    png_to_pdf(temp_pngs)


#If you sadly only have a single-core CPU, this is what is called
#instead of the multiProcess() function
def singleProcess(cpus):
    temp_pngs = pdf_to_png(thread_arg=cpus)
    invert_color(temp_pngs)
    for File in os.listdir("."):
        if File.endswith(".png"):
            black_to_grey(File)
    png_to_pdf(temp_pngs)


#Simple main fuction.
def pdfdarkmode():
    cpus = mp.cpu_count()
    if cpus == 1:
        singleProcess(cpus)
    else:
        multiProcess(cpus)


if __name__ == "__main__":
    multiProcess()