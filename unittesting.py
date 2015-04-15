__author__ = 'hofmann'

import sys
import logging
import unittest
import os
from loggingwrapper import LoggingWrapper


class DefaultLogginWrapper(unittest.TestCase):
	_expected_output_format = "{level}: [{name}] {msg}"
	log_file_path = 'unittest_out.log'
	log_file_path2 = 'unittest_out2.log'


class StdErrLoggingWrapper(DefaultLogginWrapper):
	def setUp(self):
		self.log = LoggingWrapper("StdErrLog", stream=sys.stderr)

	def tearDown(self):
		self.log.close()
		self.log = None


class StdOutLoggingWrapper(DefaultLogginWrapper):
	def setUp(self):
		self.log = LoggingWrapper("StdOutLog", stream=sys.stdout)

	def tearDown(self):
		self.log.close()
		self.log = None


class FilePathLoggingWrapper(DefaultLogginWrapper):
	def setUp(self):
		self.log = LoggingWrapper("FilePathLog", stream=None)
		self.log.set_log_file(FilePathLoggingWrapper.log_file_path)

	def tearDown(self):
		self.log.close()
		self.log = None
		os.remove(FilePathLoggingWrapper.log_file_path)


class FileStreamLoggingWrapper(DefaultLogginWrapper):
	def setUp(self):
		self.file_stream = open(FilePathLoggingWrapper.log_file_path, 'a')
		self.log = LoggingWrapper("FileStreamLog", stream=None)
		self.log.set_log_file(self.file_stream)

	def tearDown(self):
		self.log.close()
		self.log = None
		self.file_stream.close()
		self.file_stream = None
		if os.path.exists(FilePathLoggingWrapper.log_file_path):
			os.remove(FilePathLoggingWrapper.log_file_path)


class FilePathSetLogFileLoggingWrapper(FilePathLoggingWrapper):
	def runTest(self):
		self.log.set_log_file(FilePathSetLogFileLoggingWrapper.log_file_path2)


class TestSameLabelStdErrLoggingWrapper(StdErrLoggingWrapper):
	def runTest(self):
		if not hasattr(sys.stderr, "getvalue"):
			self.fail("Buffered mode required!")

		label = self.log.get_label()
		self.log2 = LoggingWrapper(label, stream=sys.stderr)
		self.log.info("log")
		self.log2.info("log2")

		sys.stderr.seek(0)
		output = sys.stderr.readline().strip()
		self.assertTrue(output.endswith(TestSameLabelStdErrLoggingWrapper._expected_output_format.format(
			level='INFO', name=self.log.get_label(), msg="log")), "'{}'".format(output))

		output = sys.stderr.readline().strip()
		self.assertTrue(output.endswith(TestSameLabelStdErrLoggingWrapper._expected_output_format.format(
			level='INFO', name=self.log2.get_label(), msg="log2")),  "'{}'".format(output))

		output = sys.stderr.readline().strip()
		self.assertEquals(output, "")
		self.log2.close()


class TestStdErrOutputLoggingWrapperMethods(StdErrLoggingWrapper):
	def runTest(self):
		if not hasattr(sys.stderr, "getvalue"):
			self.fail("Buffered mode required!")

		self.log.set_level(logging.DEBUG)

		expected_output = TestStdErrOutputLoggingWrapperMethods._expected_output_format
		messages = [
			(self.log.critical, "CRITICAL"),
			(self.log.error, "ERROR"),
			(self.log.warning, "WARNING"),
			(self.log.info, "INFO"),
			(self.log.debug, "DEBUG"),
			]
		for method, msg in messages:
			method(msg)

		sys.stderr.seek(0)
		for method, msg in messages:
			output = sys.stderr.readline().strip()
			self.assertTrue(output.endswith(expected_output.format(
				level=msg, name=self.log.get_label(), msg=msg)), "output: '{}' != '{}'".format(output, msg))

		# if TestLoggingWrapperMethods.log_file_path:
		# 	log3 = LoggingWrapper("l3", stream=None)
		# 	with open(TestLoggingWrapperMethods.log_file_path, 'a') as log_file_handle:
		# 		log3.set_log_file(log_file_handle)
		# 		log3.info("Test1")
		# 		list_of_methods = [log3.info, log3.debug, log3.warning, log3.error, log3.info, log3.critical]
		# 		count = 2
		# 		for methods in list_of_methods:
		# 			methods("Test{}".format(count))
		# 			count += 1
		# 		try:
		# 			raise TypeError("Test{}".format(count))
		# 		except TypeError:
		# 			log3.exception("Test{}".format(count))
		# 	log3.close()


if __name__ == '__main__':
	# TODO: test for logfile output then compare
	suite0 = unittest.TestLoader().loadTestsFromTestCase(FilePathSetLogFileLoggingWrapper)
	suite1 = unittest.TestLoader().loadTestsFromTestCase(TestSameLabelStdErrLoggingWrapper)
	suite2 = unittest.TestLoader().loadTestsFromTestCase(TestStdErrOutputLoggingWrapperMethods)
	alltests = unittest.TestSuite([suite0, suite1, suite2])
	unittest.TextTestRunner(verbosity=2, buffer=True).run(alltests)
