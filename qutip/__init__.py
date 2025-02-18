# This file is part of QuTiP: Quantum Toolbox in Python.
#
#    Copyright (c) 2011 and later, Paul D. Nation and Robert J. Johansson.
#    All rights reserved.
#
#    Redistribution and use in source and binary forms, with or without
#    modification, are permitted provided that the following conditions are
#    met:
#
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
#    3. Neither the name of the QuTiP: Quantum Toolbox in Python nor the names
#       of its contributors may be used to endorse or promote products derived
#       from this software without specific prior written permission.
#
#    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#    "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#    LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
#    PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#    HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#    SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#    LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#    DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#    THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#    OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
###############################################################################
import os
import warnings

import qutip.settings
import qutip.version
from qutip.version import version as __version__

# -----------------------------------------------------------------------------
# Check if we're in IPython.
try:
    __IPYTHON__
    qutip.settings.ipython = True
except NameError:
    qutip.settings.ipython = False


# -----------------------------------------------------------------------------
# Look to see if we are running with OPENMP
#
# Set environ variable to determin if running in parallel mode
# (i.e. in parfor or parallel_map)
os.environ['QUTIP_IN_PARALLEL'] = 'FALSE'

try:
    from qutip.cy.openmp.parfuncs import spmv_csr_openmp
except ImportError:
    qutip.settings.has_openmp = False
else:
    qutip.settings.has_openmp = True
    # See Pull #652 for why this is here.
    os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

import platform
from qutip.utilities import _blas_info
qutip.settings.eigh_unsafe = (_blas_info() == "OPENBLAS" and
                              platform.system() == 'Darwin')
del platform, _blas_info
# -----------------------------------------------------------------------------
# setup the cython environment
#
try:
    import Cython as _Cython
except ImportError:
    pass
else:
    from qutip.utilities import _version2int
    _cy_require = "0.29.20"
    if _version2int(_Cython.__version__) < _version2int(_cy_require):
        warnings.warn(
            "Old version of Cython detected: needed {}, got {}."
            .format(_cy_require, _Cython.__version__)
        )
    # Setup pyximport
    import qutip.cy.pyxbuilder as _pyxbuilder
    _pyxbuilder.install()
    del _pyxbuilder, _Cython, _version2int


# -----------------------------------------------------------------------------
# cpu/process configuration
#
import multiprocessing

# Check if environ flag for qutip processes is set
if 'QUTIP_NUM_PROCESSES' in os.environ:
    qutip.settings.num_cpus = int(os.environ['QUTIP_NUM_PROCESSES'])
else:
    os.environ['QUTIP_NUM_PROCESSES'] = str(qutip.settings.num_cpus)

if qutip.settings.num_cpus == 0:
    # if num_cpu is 0 set it to the available number of cores
    import qutip.hardware_info
    info = qutip.hardware_info.hardware_info()
    if 'cpus' in info:
        qutip.settings.num_cpus = info['cpus']
    else:
        try:
            qutip.settings.num_cpus = multiprocessing.cpu_count()
        except NotImplementedError:
            qutip.settings.num_cpus = 1

del multiprocessing


# Find MKL library if it exists
import qutip._mkl


# -----------------------------------------------------------------------------
# Check that import modules are compatible with requested configuration
#

# Check for Matplotlib
try:
    import matplotlib
except ImportError:
    warnings.warn("matplotlib not found: Graphics will not work.")
else:
    del matplotlib


# -----------------------------------------------------------------------------
# Load modules
#

# core
from qutip.qobj import *
from qutip.qobjevo import *
from qutip.states import *
from qutip.operators import *
from qutip.expect import *
from qutip.tensor import *
from qutip.superoperator import *
from qutip.superop_reps import *
from qutip.subsystem_apply import *
from qutip.graph import *

# graphics
from qutip.bloch import *
from qutip.visualization import *
from qutip.orbital import *
from qutip.bloch3d import *
from qutip.matplotlib_utilities import *

# library functions
from qutip.tomography import *
from qutip.wigner import *
from qutip.random_objects import *
from qutip.simdiag import *
from qutip.entropy import *
from qutip.metrics import *
from qutip.partial_transpose import *
from qutip.permute import *
from qutip.continuous_variables import *
from qutip.distributions import *
from qutip.three_level_atom import *

# evolution
from qutip.solver import *
from qutip.rhs_generate import *
from qutip.mesolve import *
from qutip.sesolve import *
from qutip.mcsolve import *
from qutip.stochastic import *
from qutip.essolve import *
from qutip.eseries import *
from qutip.propagator import *
from qutip.floquet import *
from qutip.bloch_redfield import *
from qutip.cy.br_tensor import bloch_redfield_tensor
from qutip.steadystate import *
from qutip.correlation import *
from qutip.countstat import *
from qutip.rcsolve import *
from qutip.nonmarkov import *
from qutip.interpolate import *
from qutip.scattering import *

# lattice models
from qutip.lattice import *
from qutip.topology import *

########################################################################
# This section exists only for the deprecation warning of qip importation.
# It can be deleted for a major release.

# quantum information
from qutip.qip import *
########################################################################

# utilities
from qutip.parallel import *
from qutip.utilities import *
from qutip.fileio import *
from qutip.about import *
from qutip.cite import *

# -----------------------------------------------------------------------------
# Load user configuration if present: override defaults.
#
import qutip.configrc
has_rc, rc_file = qutip.configrc.has_qutip_rc()

# Read the OpenMP threshold out if it already exists, or calibrate and save it
# if it doesn't.
if qutip.settings.has_openmp:
    _calibrate_openmp = qutip.settings.num_cpus > 1
    if has_rc:
        _calibrate_openmp = (
            _calibrate_openmp
            and not qutip.configrc.has_rc_key('openmp_thresh', rc_file=rc_file)
        )
    else:
        qutip.configrc.generate_qutiprc()
        has_rc, rc_file = qutip.configrc.has_qutip_rc()
    if _calibrate_openmp:
        print('Calibrating OpenMP threshold...')
        from qutip.cy.openmp.bench_openmp import calculate_openmp_thresh
        thresh = calculate_openmp_thresh()
        qutip.configrc.write_rc_key('openmp_thresh', thresh, rc_file=rc_file)
        del calculate_openmp_thresh

# Load the config file
if has_rc:
    qutip.configrc.load_rc_config(rc_file)

# -----------------------------------------------------------------------------
# Clean name space
#
del os, warnings
