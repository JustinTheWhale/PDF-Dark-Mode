# PDF Dark Mode

## About 

### _*NOTE:*_ This project is going under significant changes! Stay tuned for updates!

#### This is a python program that converts the white-space in PDF files to have a grey background.
#### _*NOTE:*_ This program works best with non-handwritten PDF's and PDF's without any images.

## Installation 
* ### (Windows)
* #### Download [poppler for Windows from here.](https://github.com/oschwartz10612/poppler-windows/releases/tag/v20.12.1-data)
* #### Extract the folder somewhere on your PC. 
* #### Add the path C:\<path-to-extracted-folder>\poppler-20.12.1\Library\bin in the Windows Environment PATH. 

* ### (macOS)
* #### Mac users will have to install poppler for Mac. You can do so with this [homebrew formula.](https://formulae.brew.sh/formula/poppler)

* ### (Linux)
* #### Most distributions of linux already have ```pdftoppm``` installed. If not you can check your package manager on how to install ```poppler-utils```

### Then
* #### ``` git clone https://github.com/JustinMartinezCSUSB/PDF-Dark-Mode.git ```
* #### ``` cd PDF-Dark-Mode ```
* #### ``` pip install -r requirements.txt ```
* #### Finally: ``` python pdf.py ```