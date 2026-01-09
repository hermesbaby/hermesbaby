################################################################
#                                                              #
#  This file is part of HermesBaby                             #
#                       the software engineer's typewriter     #
#                                                              #
#      https://github.com/hermesbaby                           #
#                                                              #
#  Copyright (c) 2024 Alexander Mann-Wahrenberg (basejumpa)    #
#                                                              #
#  License(s)                                                  #
#                                                              #
#  - MIT for contents used as software                         #
#  - CC BY-SA-4.0 for contents used as method or otherwise     #
#                                                              #
################################################################

"""Semantic cross-references brings meaning into Sphinx cross-references. """

from sphinx.util import logging

logger = logging.getLogger(__name__)

def setup(app):
    """Setup function for the Sphinx extension."""
    app.connect("build-finished", on_build_finished)
    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }

def on_build_finished(app, exception):
    """Event handler for the 'build-finished' event."""
    logger.info("Semantic cross-references is active.")
