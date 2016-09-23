#
# Copyright (C) 2015-2016 Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
Logging module for the Topology Modular Framework.
"""

from __future__ import unicode_literals, absolute_import
from __future__ import print_function, division

import logging
from os.path import join
from distutils.dir_util import mkpath


class BaseLogger(object):
    def __init__(self, name, level=logging.NOTSET, log_dir=None):
        self._name = name
        self._level = level
        self._log_dir = log_dir

        self.logger = logging.getLogger(name)
        self.logger.propagate = False

    def set_level(self, level):
        self._level = level
        self.logger.setLevel(self._level)

    def set_log_dir(self, log_dir):
        self._log_dir = log_dir


class PexpectLogger(BaseLogger):
    def __init__(self, *args, **kwargs):
        super(BaseLogger, self).__init__(*args, **kwargs)
        self._file_handler = None
        self.set_level(self._level)
        self.set_log_dir(self._log_dir)

    def set_log_dir(self, log_dir):
        super(BaseLogger, self).set_log_dir(log_dir)
        if self._log_dir:

            # Create file hanlder
            fh = logging.FileHandler(
                join(self._log_dir, self._name, '.log')
            )
            fh.setLevel(self._level)

            # Create formatter
            formatter = logging.Formatter('%(message)s')
            fh.setFormatter(formatter)

            # Register handler
            self.logger.addHandler(fh)
            self._file_handler = fh

        elif self._file_handler:
            self.logger.removeHandler(self._file_handler)

    def write(self, data):
        self.logger.log(self._level, data)

    def flush(self):
        pass


class LoggingManager(object):

    def __init__(self):
        """
        Framework logging manager.
        """
        self._log_dir = None
        self._log_context = None

        self._categories = [
            'library',  # name
            'platform',  # name
            'user',  # test case
            'node',  # node identifier
            'shell',  # node identifier, shell name
            'connection',  # node identifier, shell name, connection
            'pexpect',  # node identifier, shell name, connection
            'service',  # node identifier, service name, port
        ]
        self._loggers = {key: [] for key in self._categories}

        self._default_level = logging.INFO
        self._levels = {key: self._default_level for key in self._categories}

    @property
    def logging_directory(self):
        return self._log_dir

    @logging_directory.setter
    def logging_directory(self, log_dir):
        mkpath(log_dir)
        self._log_dir = log_dir
        # FIXME: Notify all "relevant categories" of a log directory change

    @property
    def logging_context(self):
        return self._log_context

    @logging_context.setter
    def logging_context(self, log_context):
        self._log_context = log_context

    def set_category_level(self, category, level):
        if category not in self._categories:
            raise ValueError(
                'Unknown category "{}"'.format(category)
            )
        self._levels[category] = level
        for logger in self._loggers[category]:
            logger.set_level(level)

    def get_logger(self, name, category):
        if category not in self._categories:
            raise ValueError(
                'Unknown category "{}" for logger {}'.format(category, name)
            )

        name = '{}.{}'.format(category, name)
        if self._log_context is not None:
            name = '{}.{}'.format(self._log_context, name)

        if category == 'pexpect':
            return PexpectLogger(
                name, self._levels[category], self._log_dir
            )

        raise NotImplementedError(
            'Category "{}" not implemented'.format(category)
        )

manager = LoggingManager()
get_logger = manager.get_logger


__all__ = [
    'manager',
    'get_logger'
]
