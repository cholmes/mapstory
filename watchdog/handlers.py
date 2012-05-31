from logging import Handler
from StringIO import StringIO


class MemoryHandler(Handler):
    """keep track of conents of logging in memory for later retrieval"""

    def __init__(self, *args, **kwargs):
        Handler.__init__(self, *args, **kwargs)
        self.buffer = StringIO()

    def emit(self, record):
        try:
            msg = self.format(record)
            if not msg.endswith('\n'):
                msg = msg + '\n'
            self.buffer.write(msg)
        except:
            self.handleError(record)

    def contents(self):
        return self.buffer.getvalue()
