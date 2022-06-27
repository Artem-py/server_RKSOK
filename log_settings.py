logger_config = {
    'version': 1,
    'disable_existing_loggers': False,
    
    'formatters': {
        'std_format': {
            'format': '{asctime} | {name} | line: {lineno} | {message}', 
            'style': '{',
        }
    },
    'handlers': {
        'file_handler': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'std_format',
            'filename': 'rksok_log.log',
            'encoding': 'UTF-8',
            'maxBytes': 100000,
            'backupCount': 10
        }
    },
    'loggers': {
        'main': {
            'level': 'DEBUG',
            'handlers': ['file_handler']
        }
    }
}