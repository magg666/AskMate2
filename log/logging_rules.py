import logging

logger = logging.getLogger(__name__)
f_handler = logging.FileHandler('log/app.log')
f_handler.setLevel(logging.ERROR)
f_format = logging.Formatter('%(asctime)s - LEVEL: %(levelname)s - '
                             'IN MODULE: %(module)s - IN FUNCTION: %(funcName)s '
                             'IN LINE: %(lineno)d - %(message)s')
f_handler.setFormatter(f_format)
logger.addHandler(f_handler)
