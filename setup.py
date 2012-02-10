import os
from setuptools import setup
import renderit

try:
    reqs = open(os.path.join(os.path.dirname(__file__),'requirements.txt')).read()
except (IOError, OSError):
    reqs = ''
    
setup(name='django-renderit',
      version=renderit.get_version(),
      description='Application that can render any object',
      author='Jose Soares',
      author_email='jose@linux.com',
      url='http://github.com/jsoa/django-renderit/',
      packages=['renderit', 'renderit.templatetags'],
      include_package_data = True,
      install_requires = reqs,
      classifiers=['Framework :: Django',
          'License :: OSI Approved :: Apache Software License',
          'Development Status :: 4 - Beta',
          'Environment :: Other Environment',
          'Programming Language :: Python',
          ],
      )
