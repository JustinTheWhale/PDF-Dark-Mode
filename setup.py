from setuptools import setup

setup(name='PdfDarkMode',
      version='1.0.5',
      description='Converts PDFs to have a grey background to be easier on the eyes',
      readme='README.md',
      author='JustinTheWhale',
      author_email='justinraymen@gmail.com',
      url='https://github.com/JustinTheWhale/PDF-Dark-Mode',
      install_requires=['opencv-python>=4.9.0.80', 'numpy>=1.26.0', 'fpdf2>=2.7.9',
                'numba>=0.59.0', 'pdf2image>=1.17.0', 'Pillow>=10.3.0',
                'pypdf>=4.0.0']
     )