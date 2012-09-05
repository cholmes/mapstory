from django.contrib.staticfiles.storage import CachedFilesMixin, StaticFilesStorage
import sys

class CachedStaticFilesStorage(CachedFilesMixin, StaticFilesStorage):

    def hashed_name(self, name, content=None):
        try:
            return CachedFilesMixin.hashed_name(self, name, content)
        except ValueError:
            print >> sys.stderr, 'error hashing %s for staticfiles' % name
            return name
