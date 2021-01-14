# PDF Dark Mode

## About 

#### This is a python program that converts the white-space in PDF files to have a grey background. It will convert all PDF files in the current directory and takes about 5-10 seconds on average. (depends on the sizef the PDF) 
#### _*NOTE:*_ This program works best with non-handwritten PDF's and PDF's without any images.

## Installation
* #### Download [poppler for Windows from here](https://github.com/oschwartz10612/poppler-windows/releases/tag/v20.12.1-data)
* #### Extract the folder somewhere on your PC. 
* #### Add the path C:\<path-to-extracted-folder>\poppler-20.12.1\Library\bin in the Windows Environment PATH. 

### Using python virtual environment
* #### ``` git clone https://github.com/JustinMartinezCSUSB/PDF-Dark-Mode.git ```
* #### ``` python -m venv  PDF-Dark-Mode ```
* #### ``` cd PDF-Dark-Mode ```
* #### ``` Scripts/activate.bat ``` if using cmd or ``` Scripts/activate.ps1 ``` if using powershell 
* #### ``` pip install -r requirements.txt ```
* #### Move the PDF files you want converted into this directory 
* #### Finally: ``` python pdf.py ```

### Without python virtual environment
* #### ``` git clone https://github.com/JustinMartinezCSUSB/PDF-Dark-Mode.git ```
* #### ``` cd PDF-Dark-Mode ```
* #### ``` pip install -r requirements.txt ```
* #### Move the PDF files you want converted into this directory 
* #### Finally: ``` python pdf.py ```