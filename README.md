# PDF-Dark-Mode-No-GUI-
Same as GUI version but does not let you choose the directory, instead it converts all PDF's in the current directory

Sick of getting your eyeballs burned out by white PDF's? Try this. 
________________________________________________________________________________

This python program converts white-backgrounds in PDF files to grey-ish "Dark Mode" background.

This .py file requires the following:
 * pdf2image
 * fpdf
 * PyPDF2
 * OpenCV2
  
  You can use pip to install pdf2image, fpdf, PyPDF2, and OpenCV2 via:
  
  
    pip install pdf2image fpdf pypdf2 opencv-python
    
    
You then need to add the included folder "poppler-0.68.0/bin" to your Windows Enviroment PATH
    
    
    
# Usage
   
   Once you have all of those modules simply run "python pdfdarkmode.py". Make sure you ave the PDF's you want to convert in the same directory.
