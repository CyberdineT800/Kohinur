# import logging

# class WarningAndCriticalFilter(logging.Filter):
#     def filter(self, record):
#         return record.levelno in (logging.WARNING, logging.CRITICAL)

# logger = logging.getLogger()

# logger.setLevel(logging.NOTSET)

# console_handler = logging.StreamHandler()
# console_handler.setLevel(logging.NOTSET)

# console_handler.addFilter(WarningAndCriticalFilter())

# formatter = logging.Formatter(u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s')
# console_handler.setFormatter(formatter)

# logger.addHandler(console_handler)

import logging


logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.WARNING,
                    # level=logging.DEBUG,
                    )

# logger = logging.getLogger('dispatcher.py')
# print(logger)
# logger.setLevel(logging.CRITICAL)
# logger = logging.getLogger('dispatcher.py')
# print(logger)