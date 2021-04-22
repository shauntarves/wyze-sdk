import logging
from logging import NullHandler

# By default, do not force any logging by the library. If you want to see the
# log messages in your scripts, add the following to the top of your script:
#   import wyze_sdk
#   wyze_sdk.set_stream_logger(__name__)
#   OR
#   wyze_sdk.set_file_logger(__name__, '/tmp/log')
logging.getLogger(__name__).addHandler(NullHandler())
