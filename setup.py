from setuptools import (
    setup,
    find_packages,
)


def get_requirements(filenames):
    r_total = []
    for filename in filenames:
        with open(filename) as f:
            r_local = f.read().splitlines()
            r_total.extend(r_local)
    return r_total


setup(
    name='bulk_chain',
    version='0.24.1',
    python_requires=">=3.6",
    description='A lightweight, no-strings-attached Chain-of-Thought framework for your LLM, '
                'ensuring reliable results for bulk input requests.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/nicolay-r/bulk-chain',
    author='Nicolay Rusnachenko',
    author_email='rusnicolay@gmail.com',
    license='MIT License',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Text Processing :: Linguistic',
    ],
    keywords='natural language processing, '
             'chain-of-thought, '
             'reasoning',
    packages=find_packages(),
    install_requires=get_requirements(['dependencies.txt'])
)