from pdf2image import convert_from_path
from fpdf import FPDF
from PyPDF2 import PdfFileMerger
import os
import cv2
import numpy as np


def pdf_to_png():
    pdf_names = []
    for File in os.listdir('.'):
        if File.endswith('.pdf'):
            try:
                pages = convert_from_path(File)
                new_name = File[:-4]
                temp_list = []
                for page in pages:
                    page.save('%s-page%d.png' % (new_name, pages.index(page)), 'PNG')
                    temp_list.append('%s-page%d.png' % (new_name, pages.index(page)))
                temp_array = np.array(temp_list)
                pdf_names.append(temp_array)
            except OSError:
                print("Could not covert " + File + " to PNG for processing - file(s) may be missing or corrupt")
    print("Successfully converted the following PDF's to PNG")
    print(*pdf_names, sep=", ")
    return pdf_names


def invert_color(png_array):
    for x in range(len(png_array)):
        for png in range(len(png_array[x].tolist())):
            image = cv2.imread(png_array[x].tolist()[png])
            image_inverted = cv2.bitwise_not(image)
            cv2.imwrite(png_array[x].tolist()[png], image_inverted)


def black_to_grey():
    png_names = []
    for File in os.listdir('.'):
        if File.endswith('.png'):
            try:
                color_array = cv2.imread(File)
                length = (color_array.shape[0] - 1)
                width = (color_array.shape[1] - 1)
                for i in range(0, length):
                    for j in range(0, width):
                        if color_array[i, j].tolist() == [0, 0, 0]:
                            color_array[i, j] = [75, 75, 75]
                cv2.imwrite(File, color_array)
                png_names.append(File)
            except OSError:
                print("Could not convert black pixels in" + File + " to grey")
    print("Successfully converted the following PNG's blacks to grey")
    print(*png_names, sep=" ,")


def np_array_tolist(my_np_array):
    my_list = []
    for a in range(len(my_np_array)):
        tuna = my_np_array[a].tolist()
        my_list.extend(tuna)
    return my_list


def remove_pngs():
    for File in os.listdir('.'):
        if File.endswith(".png"):
            os.remove(File)
    print("Successfully removed temporary PNG's")


def dm_file_list():
    file_list = []
    for File in os.listdir('.'):
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
    b = 0
    while b < len(darkmode_list):
        start_end_list = get_start_end(darkmode_list, darkmode_list[b][:-24])
        start = start_end_list[0]
        end = start_end_list[len(start_end_list)-1]
        b = end + 1
        items = tuple(darkmode_list[start:b])
        group_list.append(items)
    return group_list
    

def repack(darkmode_pdfs):
    for i in range(len(darkmode_pdfs)):
        merger = PdfFileMerger()        
        for j in range(len(darkmode_pdfs[i])):
            merger.append(darkmode_pdfs[i][j])
        merger.write(darkmode_pdfs[i][j][:-24] + "_darkmode.pdf")
        merger.close()
        pdfs = []

def remove_pages_pdfs():
    for File in os.listdir('.'):
        if "temp_darkmode.pdf" in File:
            os.remove(File)
    print("Succesfully cleaned up temp PNG's")

def png_to_pdf(png_np_array):
    for x in range(len(png_np_array)):
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.image(png_np_array[x], 0, 0, 210, 300)
            pdf.output(png_np_array[x][:-4] + "_temp_darkmode.pdf", "F")
            pdf.close()
            print("Successfully converted" + png_np_array[x][:-4] +  ".pdf")
        except OSError:
            print("There was an issue converting the PNG's back into PDF's")
    print("Successfully converted all PNG's to PDF's - Removing PNG's. . . . . . ")
    remove_pngs()
    print("Successfully removed all temporary PNG's")
    repack(get_groups(dm_file_list())) # Repacks back into PDF's
    remove_pages_pdfs()
    print("Successfully cleaned up all temp PDF files")


np_array = pdf_to_png() # Converts PDF to PNG
invert_color(np_array) # Makes every white pixel black
black_to_grey() # makes every black pixel grey
np_list = np_array_tolist(np_array) #makes list easier to work with
png_to_pdf(np_list) # converts PNG's to PDF