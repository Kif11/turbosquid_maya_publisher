import sys
import time
import datetime

class Logger(object):

	def __init__ (self, name='', debug=False, log_time=False, log_type=True):

		self._INFO = '[+]'
		self._WARNING = '[-]'
		self._ERROR = '[!]'
		self._DEBUG = '[D]'
		self._SEP_CHAR = '-'
		self.name = name
		self.log_time = log_time
		self.log_type = log_type

		self.debug_active = debug

	def make_msg(self, msg, msg_type = ''):
		cur_time = datetime.datetime.now().strftime('%H:%M:%S')
		if self.log_time:
			msg = '%s %s' %(cur_time, msg)
		if self.name:
			msg = '%s: %s' %(self.name, msg)
		if self.log_type:
			msg = '%s %s' %(msg_type, msg)

		return msg

	def log(self, msg):
		print msg
		self.flush();

	def info(self, msg):
		msg = self.make_msg(msg, self._INFO)
		self.log(msg)

	def warning(self, msg):
		msg = self.make_msg(msg, self._WARNING)
		self.log(msg)

	def debug(self, msg):
		if (self.debug_active):
			msg = self.make_msg(msg, self._DEBUG)
			self.log(msg)
		else:
			pass

	def error(self, msg):
		msg = self.make_msg(msg, self._ERROR)
		self.log(msg)

		# raise NameError('Error reported, aborting render script!')

	def line(self):
		"""
		Print separation line on 80 chars.
		"""
		self.log(self._SEP_CHAR * 80)

	def flush(self):
		sys.stdout.flush()
		sys.stderr.flush()
