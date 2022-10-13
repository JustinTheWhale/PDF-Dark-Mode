from setuptools import setup

setup(name='PDF-Dark-Mode',
      version='1.0.4',
      description='Converts PDFs to have a grey background to be easier on the eyes',
      author='JustinTheWhale',
      author_email='justinraymen@gmail.com',
      url='https://github.com/JustinTheWhale/PDF-Dark-Mode',
      install_requires=['opencv-python', 'numpy', 'fpdf', 'numba',
                'pdf2image', 'Pillow', 'PyPDF2']
     )