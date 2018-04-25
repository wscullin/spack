##############################################################################
# Copyright (c) 2013-2018, Lawrence Livermore National Security, LLC.
# Produced at the Lawrence Livermore National Laboratory.
#
# This file is part of Spack.
# Created by Todd Gamblin, tgamblin@llnl.gov, All rights reserved.
# LLNL-CODE-647188
#
# For details, see https://github.com/spack/spack
# Please also see the NOTICE and LICENSE files for our notice and the LGPL.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License (as
# published by the Free Software Foundation) version 2.1, February 1999.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the IMPLIED WARRANTY OF
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the terms and
# conditions of the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##############################################################################
##########################################################################
# Copyright (c) 2015-2018 Krell Institute. All Rights Reserved.
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA  02111-1307  USA
##########################################################################

from spack import *
import os


class CbtfArgonavis(CMakePackage):
    """CBTF Argo Navis project contains the CUDA collector and supporting
       libraries that was done as a result of a DOE SBIR grant.

    """
    homepage = "http://sourceforge.net/p/cbtf/wiki/Home/"

    version('1.9.1', branch='master',
            git='https://github.com/OpenSpeedShop/cbtf-argonavis.git')

    variant('cti', default=False,
            description="Build MRNet with the CTI startup option")
    variant('crayfe', default=False,
            description="build only the FE tool using the runtime_dir \
                         to point to target build.")
    variant('runtime', default=False,
            description="build only the runtime libraries and collectors.")
    variant('build_type', default='None', values=('None'),
            description='CMake build type')

    depends_on("cmake@3.0.2:", type='build')
    depends_on("boost@1.50.0:")
    depends_on("papi")
    depends_on("libmonitor")
    depends_on("mrnet@5.0.1:+lwthreads")
    depends_on("mrnet@5.0.1:+cti", when='+cti')
    depends_on("cbtf")
    depends_on("cbtf+cti", when='+cti')
    depends_on("cbtf+runtime", when='+runtime')
    depends_on("cbtf-krell")
    depends_on("cbtf-krell+cti", when="+cti")
    depends_on("cbtf-krell+runtime", when="+runtime")
    depends_on("cuda")

    parallel = False

    build_directory = 'build_cbtf_argonavis'

    def cmake_args(self):
        spec = self.spec
        compile_flags = "-O2 -g"

        cmake_args = [
            '-DCMAKE_CXX_FLAGS=%s'         % compile_flags,
            '-DCMAKE_C_FLAGS=%s'           % compile_flags,
            '-DCUDA_DIR=%s' % spec['cuda'].prefix,
            '-DCUDA_INSTALL_PATH=%s' % spec['cuda'].prefix,
            '-DCUDA_TOOLKIT_ROOT_DIR=%s' % spec['cuda'].prefix,
            '-DCUPTI_DIR=%s' % spec['cuda'].prefix.extras.CUPTI,
            '-DCUPTI_ROOT=%s' % spec['cuda'].prefix.extras.CUPTI,
            '-DPAPI_ROOT=%s' % spec['papi'].prefix,
            '-DCBTF_DIR=%s' % spec['cbtf'].prefix,
            '-DCBTF_KRELL_DIR=%s' % spec['cbtf-krell'].prefix,
            '-DBOOST_ROOT=%s' % spec['boost'].prefix,
            '-DBoost_DIR=%s' % spec['boost'].prefix,
            '-DBOOST_LIBRARYDIR=%s' % spec['boost'].prefix.lib,
            '-DMRNET_DIR=%s' % spec['mrnet'].prefix,
            '-DLIBMONITOR_DIR=%s' % spec['libmonitor'].prefix,
            '-DBoost_NO_SYSTEM_PATHS=ON']

        return cmake_args

    def setup_environment(self, spack_env, run_env):
        """Set up the compile and runtime environments for a package."""

        if os.environ.get('LD_LIBRARY_PATH'):
            cupti_path = self.spec['cuda'].prefix + '/extras/CUPTI/lib64'
            os.environ['LD_LIBRARY_PATH'] += cupti_path
        else:
            os.environ['LD_LIBRARY_PATH'] = cupti_path

        run_env.prepend_path(
            'LD_LIBRARY_PATH',
            self.spec['cuda'].prefix + '/extras/CUPTI/lib64')
        spack_env.prepend_path(
            'LD_LIBRARY_PATH',
            self.spec['cuda'].prefix + '/extras/CUPTI/lib64')
