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

"""Checks for updates"""

def _build_finished(app, exception):
    if exception is None:
        msg = "hermesbaby.update: Build finished successfully."
    else:
        msg = f"hermesbaby.update: Build finished with exception: {exception}"

    print(msg)


def setup(app):
    app.connect("build-finished", _build_finished)
    return {
        'version': '1.0',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
