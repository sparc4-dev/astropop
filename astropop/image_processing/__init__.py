# Licensed under a 3-clause BSD style license - see LICENSE.rst

from .ccd_processing import *
from .imarith import *
from .register import *

register_available_methods = [None, 'fft']
combine_available_methods = ['median', 'sum', 'average']
