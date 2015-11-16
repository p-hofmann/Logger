LoggingWrapper
=======

Wrapper for the logging module

## Example:

	class Example(DefaultLogging):
		def __init__(self, logfile=None, verbose=False, debug=False):
			super(Example, self).__init__(logfile=logfile, verbose=verbose, debug=debug)
	
		def test(self):
			self._logger.info("test")
