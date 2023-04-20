# Copyright (C) 2020-2021 
# SPDX-License-Identifier: Apache-2.0

"""Test abby.logger
"""

from abby.logger import setup_logger


def test_logger():
    """Test to setup Python logger."""
    log = setup_logger()
    log.debug("test message")
