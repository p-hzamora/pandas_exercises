import logging
import time
from typing import Callable





def logger_decorator(func: Callable) -> Callable:
    """
        Decorator to log execution time and exceptions to a file.

        params:
                func: Function to be decorated
    """
    # Global project variable for logger level
    LOG_LEVEL = logging.DEBUG

    # Possible logging levels and their values:
    # logging.CRITICAL - 50
    # logging.ERROR - 40
    # logging.WARNING - 30
    # logging.INFO - 20
    # logging.DEBUG - 10
    # logging.NOTSET - 0

    # Create logger
    logger = logging.getLogger(__name__)
    logger.setLevel(LOG_LEVEL)

    # Create file handler
    file_handler = logging.FileHandler('log.csv', mode='a')
    file_handler.setLevel(LOG_LEVEL)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', 
                                    datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)

    # Add file handler to logger
    logger.addHandler(file_handler)

    def wrapper(*args, **kwargs):
        try:
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            execution_time = (end_time - start_time) * 1000

            # Get function signature and arguments
            args_repr = [repr(a) for a in args]
            kwargs_repr = [f'{k}={v!r}' for k, v in kwargs.items()]
            signature = ', '.join(args_repr + kwargs_repr)

            if len(signature) == 0:
                signature = 'No arguments provided'

            # Log 
            logger.info(f'{func.__name__} - {signature} - {execution_time:.3f} ms')

            return result
        
        except Exception as e:
            # Log exception
            logger.error(str(e))
            raise e

    return wrapper



if __name__ == '__main__':
    @logger_decorator
    def my_function():
        # Code for your function here
        print("Hello, World!") 
        pass

    my_function()

