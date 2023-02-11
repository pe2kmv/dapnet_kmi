import logging
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')


def setup_logger(name, log_file, level=logging.DEBUG):
	handler = logging.FileHandler(log_file)
	handler.setFormatter(formatter)

	logger = logging.getLogger(name)
	logger.setLevel(level)
	logger.addHandler(handler)

	return(logger)

# main logger
main_logger = setup_logger('main_logger', '/var/log/kmi_main.log')

# KMI message logger
msg_logger = setup_logger('kmi_msg_logger', '/var/log/kmi_msg.log')

# KMI error logger
error_logger = setup_logger('kmi_err_logger','/var/log/kmi_err.log')
