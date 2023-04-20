# Copyright (C) 2020-2021 
# SPDX-License-Identifier: Apache-2.0

"""
*Pretty logging for nice command line programs.*

When using tqdm (progress bars) with Python logging, text output is broken.
This module implements a custom logger that solves this issue.

This logger also colors output and set the right verbosity level.
"""

import logging

from tqdm import tqdm


class TqdmLoggingHandler(logging.Handler):
    """Define custom logging handler that does not break tqdm output"""

    def emit(self, record):
        """Log the record with tqdm print"""
        try:
            msg = self.format(record)
            tqdm.write(msg)
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)


def setup_logger(name="abby", quiet=False, debug=False) -> logging.Logger:
    """Create Python logging.Logger with colors and tqdm support.

    If you want to apply this logger configuration to abby submodules, you
    should name it ``abby`` as ``abby.something`` will inherit configuration.

    Default verbosity is INFO, WARNING, ERRORS and CRITICAL. If quiet, show
    only ERRORS and CRITICAL. If debug, show everything.

    :param name: name of the logger, should be the root of all other logger
    :type name: str, optional
    :param quiet: only print warning and errors, defaults to False
    :type quiet: bool, optional
    :param debug: print debugging information, defaults to False
    :type debug: bool, optional
    :return: custom logger
    :rtype: logging.Logger
    """
    if not quiet:
        verbosity = 20 if not debug else 10
    else:
        verbosity = 40

    # Change log format
    formatter = logging.Formatter(
        fmt="\033[90m%(asctime)s\033[1;0m %(levelname)s [%(name)s] %(message)s"
    )
    logger = logging.getLogger(name)

    # Change level names and set level
    logging.addLevelName(logging.INFO, "\033[1;36mINFO\033[1;0m")
    logging.addLevelName(logging.WARNING, "\033[1;33mWARNING\033[1;0m")
    logging.addLevelName(logging.ERROR, "\033[1;91mERROR\033[1;0m")
    logging.addLevelName(logging.DEBUG, "\033[1;37mDEBUG\033[1;0m")
    logger.setLevel(verbosity)

    # Custom handler
    handler = TqdmLoggingHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
