from pdf2image import convert_from_path
from PyPDF2 import PdfFileMerger
import multiprocessing as mp
from fpdf import FPDF
import cv2
import os



def pdf_to_png(dpi_arg=300, thread_arg=1):
    arg_dict = locals()
    dpi_count = arg_dict['dpi_arg']
    threads = arg_dict['thread_arg']
    png_names = []
    page_count = 0
    for File in os.listdir("."):
        if File.endswith(".pdf"):
                pages = convert_from_path(File, dpi=dpi_count, thread_count=threads)
                new_name = File[:-4]
                for page in pages:
                    page.save('%s-page%d.png' % (new_name, pages.index(page)), 'PNG')
                    png_names.append('%s-page%d.png' % (new_name, pages.index(page)))
                    page_count += 1
    return png_names


def invert_color(pngs_white):
    for i in range(len(pngs_white)):
        image = cv2.imread(pngs_white[i])
        image_inverted = cv2.bitwise_not(image)
        cv2.imwrite(pngs_white[i], image_inverted)
        

def black_to_grey(File):
    color_array = cv2.imread(File)
    length = (color_array.shape[0] - 1)
    width = (color_array.shape[1] - 1)
    for i in range(0, length):
        for j in range(0, width):
            if color_array[i, j].tolist() == [0, 0, 0]:
                color_array[i, j] = [100, 100, 100]
    cv2.imwrite(File, color_array)


def darkmode_files():
    file_list = []
    for File in os.listdir("."):
        if "_darkmode" in File:
            file_list.append(File)
    return sorted(file_list)


def get_start_end(darkmode_list, element):
    index_list = []
    tuple_list = []
    for i in enumerate(darkmode_list):
        tuple_list.append(i)
    for j in range(len(tuple_list)):
        if element in tuple_list[j][1]:
            index_list.append(tuple_list[j][0])
    return index_list
    

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


def remove_temp_pdfs():
    for File in os.listdir("."):
        if "temp_darkmode.pdf" in File:
            os.remove(File)


def remove_pngs():
    for File in os.listdir("."):
        if File.endswith(".png"):
            os.remove(File)


def repack(darkmode_pdfs):
    for i in range(len(darkmode_pdfs)):
        merger = PdfFileMerger()        
        for j in range(len(darkmode_pdfs[i])):
            merger.append(darkmode_pdfs[i][j])
        merger.write(darkmode_pdfs[i][j][:-24] + "_darkmode.pdf")
        merger.close()


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


def make_batches(process_list, cpus):
    batches = [process_list[i:i + cpus] for i in range(0, len(process_list), cpus)]
    return batches


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


def singleProcess(cpus):
    temp_pngs = pdf_to_png(thread_arg=cpus)
    invert_color(temp_pngs)
    for File in os.listdir("."):
        if File.endswith(".png"):
            black_to_grey(File)
    png_to_pdf(temp_pngs)


def pdfdarkmode():
    cpus = mp.cpu_count()
    if cpus == 1:
        singleProcess(cpus)
    else:
        multiProcess(cpus)


if __name__ == "__main__":
    mydict = mp_test()
    print(mydict.keys())
    print(mydict.values())