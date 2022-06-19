from setuptools import setup, find_packages
from io import open
from os import path

import pathlib
# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# automatically captured required modules for install_requires in requirements.txt
# with open(path.join(HERE, 'requirements.txt'), encoding='utf-16') as f:
#     all_reqs = f.read().split('\n')
#print(all_reqs)
# install_requires = [x.strip() for x in all_reqs if ('git+' not in x) and (
#     not x.startswith('#')) and (not x.startswith('-'))]
# dependency_links = [x.strip().replace('git+', '') for x in all_reqs \
#                     if 'git+' not in x]
setup (
 name = 'slide_extractor',
 description = 'A simple commandline app to extract slides from videos,lectures and presentations',
 version = '1.0.6',
 packages = find_packages(), # list of all packages
 install_requires = ['colorama', 'numpy', 'opencv-python', 'Pillow', 'tqdm'],
 python_requires='>=3.5', # any python greater than 2.7
 entry_points={
        'console_scripts':
        ['slide-extractor=slide_extractor.__main__:main']
},
 author="Vivek Anand, Ashish Manglani",
 keywords=['slide-extractor', 'slide_extractor', 'extractor', 'slide', 'slide extractor'],
 long_description=README,
 long_description_content_type="text/markdown",
 license='MIT',
 url='https://github.com/Slide-extractor-beta/slide-extractor',
 download_url='https://github.com/Slide-extractor-beta/slide-extractor/archive/refs/tags/v1.0.0-beta.tar.gz',
  author_email='vivek17212797@gmail.com',

)