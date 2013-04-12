# coding: utf-8
# XXX: The original author of this file is Chris Jerdonek (https://github.com/cjerdonek).
# It is included here because python-mustache started out as a fork of Pystache
# (https://github.com/defunkt/pystache), the library to which this code was
# contributed. This file will be replaced soon.
try:
	import json
except:
	import simplejson as json

import glob
import os.path
import unittest

from mustache import render

root_path = os.path.join(os.path.dirname(__file__), 'spec', 'specs')
spec_paths = glob.glob(os.path.join(root_path, '*.json'))

class MustacheSpec(unittest.TestCase):
	pass

def buildTest(testData, spec_filename):

	name = testData['name']
	description  = testData['desc']

	test_name = "%s (%s)" % (name, spec_filename)

	def test(self):
		template = testData['template']
		partials = testData.has_key('partials') and testData['partials'] or {}
		expected = testData['expected']
		data	 = testData['data']

		# Convert code strings to functions.
		new_data = {}
		for key, val in data.iteritems():
			if isinstance(val, dict) and val.get('__tag__') == 'code':
				val = eval(val['python'])
			new_data[key] = val

		actual = render(template, new_data, partials)

		message = """%s

  Template: \"""%s\"""

  Expected: %s
  Actual:   %s

  Expected: \"""%s\"""
  Actual:   \"""%s\"""
  """ % (description, template, repr(expected), repr(actual), expected, actual)

		self.assertEquals(actual, expected, message)

	# The name must begin with "test" for nosetests test discovery to work.
	name =  'test: "%s"' % test_name

	# If we don't convert unicode to str, we get the following error:
	#   "TypeError: __name__ must be set to a string object"
	test.__name__ = str(name)

	return test

for spec_path in spec_paths:

	file_name  = os.path.basename(spec_path)

	# We avoid use of the with keyword for Python 2.4 support.
	f = open(spec_path, 'r')
	try:
		spec_data = json.load(f)
	finally:
		f.close()

	tests = spec_data['tests']

	for test in tests:
		test = buildTest(test, file_name)
		setattr(MustacheSpec, test.__name__, test)
		# Prevent this variable from being interpreted as another test.
		del(test)

if __name__ == '__main__':
	unittest.main()

