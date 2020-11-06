#!/usr/bin/env python

from setuptools import setup

setup(name='tap-billwerk',
	version="0.1.0",
	description="Singer.io tap for extracting data from Billwerk API",
	author="DQ",
    	classifiers=["Programming Language :: Python :: 3 :: Only"],
    	py_modules=["tap_billwerk"],
    	install_requires=[
        	'singer-python==5.9.1',
        	'requests==2.24.0',
        	'requests-oauthlib==1.3.0',
        	'backoff==1.8.0'
    	],
    	extras_require={
        	 'dev': [
			'ipdb==0.11',
			'pylint',
             		'nose'
         	]
    	},
    	entry_points='''
    		[console_scripts]
    		tap-billwerk=tap_billwerk:main
    	''',
    	packages=['tap_billwerk'],
    	package_data = {
        	"schemas": ["tap_billwerk/schemas/*.json"]
    	},
    	include_package_data=True,
)
