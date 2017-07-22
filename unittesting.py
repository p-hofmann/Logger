__author__ = 'hofmann'

import logging
import unittest
import os
from loggingwrapper import LoggingWrapper
from io import StringIO


test_stream = StringIO()


class DefaultLogginWrapper(unittest.TestCase):
    """
    @type log: LoggingWrapper
    """
    _expected_output_format = "{level}: [{name}] {msg}"
    log_file_path = 'unittest_out.log'
    log_file_path2 = 'unittest_out2.log'

    def __init__(self, methodName='runTest'):
        super(DefaultLogginWrapper, self).__init__(methodName)
        self.log = LoggingWrapper("", stream=None)


class StreamLoggingWrapper(DefaultLogginWrapper):
    def setUp(self):
        test_stream.reset()
        self.log = LoggingWrapper("StdErrLog", stream=test_stream)

    def tearDown(self):
        test_stream.reset()
        self.log = None


class FilePathLoggingWrapper(DefaultLogginWrapper):
    def setUp(self):
        self.log = LoggingWrapper("FilePathLog", stream=None)
        self.file_handler = self.log.set_logfile(FilePathLoggingWrapper.log_file_path)

    def tearDown(self):
        self.log = None
        self.file_handler.close()
        if os.path.exists(FilePathLoggingWrapper.log_file_path):
            os.remove(FilePathLoggingWrapper.log_file_path)


class FilePathSetLogFileLoggingWrapper(FilePathLoggingWrapper):
    def runTest(self):
        self.assertIsNotNone(self.log.set_logfile(FilePathSetLogFileLoggingWrapper.log_file_path2))
        self.assertEquals(len(self.log._logger.handlers), 1)


class TestSameLabelStreamLoggingWrapper(StreamLoggingWrapper):
    def runTest(self):
        label = self.log.get_label()
        self.log2 = LoggingWrapper(label, stream=test_stream)
        self.log.info("log")
        self.log2.info("log2")
        self.assertEquals(len(self.log._logger.handlers), 1)

        test_stream.seek(0)
        output = test_stream.readline().strip()
        self.assertTrue(output.endswith(TestSameLabelStreamLoggingWrapper._expected_output_format.format(
            level='INFO', name=self.log.get_label(), msg="log")), "'{}'".format(output))

        output = test_stream.readline().strip()
        self.assertTrue(output.endswith(TestSameLabelStreamLoggingWrapper._expected_output_format.format(
            level='INFO', name=self.log2.get_label(), msg="log2")),  "'{}'".format(output))

        output = test_stream.readline().strip()
        self.assertEquals(output, "")


class TestStreamOutputLoggingWrapperMethods(StreamLoggingWrapper):
    def runTest(self):
        self.log.set_level(logging.DEBUG)

        expected_output = TestStreamOutputLoggingWrapperMethods._expected_output_format
        messages = [
            (self.log.critical, "CRITICAL"),
            (self.log.error, "ERROR"),
            (self.log.warning, "WARNING"),
            (self.log.info, "INFO"),
            (self.log.debug, "DEBUG"),
            ]

        test_stream.seek(0)
        for method, msg in messages:
            method(msg)
        self.assertEquals(len(self.log._logger.handlers), 1)

        test_stream.seek(0)
        for method, msg in messages:
            output = test_stream.readline().strip()
            self.assertTrue(
                output.endswith(expected_output.format(level=msg, name=self.log.get_label(), msg=msg)),
                "output: '{}' != '{}'".format(output, msg))


if __name__ == '__main__':
    # TODO: test for logfile output then compare
    suite0 = unittest.TestLoader().loadTestsFromTestCase(FilePathSetLogFileLoggingWrapper)
    suite1 = unittest.TestLoader().loadTestsFromTestCase(TestSameLabelStreamLoggingWrapper)
    suite2 = unittest.TestLoader().loadTestsFromTestCase(TestStreamOutputLoggingWrapperMethods)
    alltests = unittest.TestSuite([suite0, suite1, suite2])
    unittest.TextTestRunner(verbosity=2).run(alltests)
