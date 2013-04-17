from distutils.core import setup
setup(
    name = 'mustache',
    packages = ['mustache'],
    version = '0.1.3',
    description = 'Mustache templating in Python',
    author = 'Peter Downs',
    author_email = 'peterldowns@gmail.com',
    url = 'https://github.com/peterldowns/python-mustache',
    download_url = 'https://github.com/peterldowns/python-mustache/tarball/v0.1.3',
    install_requirements = open('requirements.txt').read(),
    extras_require = {
      'test' : open('tests/requirements.txt').read(),
    },
    keywords = [
        'templating',
        'template',
        'mustache',
        'web'],
    classifiers = [
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Markup'],
)
