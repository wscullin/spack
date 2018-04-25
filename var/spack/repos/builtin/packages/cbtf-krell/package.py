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
import spack
import spack.store


class CbtfKrell(CMakePackage):
    """CBTF Krell project contains the Krell Institute contributions to the
       CBTF project.  These contributions include many performance data
       collectors and support libraries as well as some example tools
       that drive the data collection at HPC levels of scale.

    """
    homepage = "http://sourceforge.net/p/cbtf/wiki/Home/"

    version('1.9.1', branch='master',
            git='https://github.com/OpenSpeedShop/cbtf-krell.git')

    # MPI variants
    variant('openmpi', default=False,
            description="Build mpi experiment collector for openmpi MPI..")
    variant('mpt', default=False,
            description="Build mpi experiment collector for SGI MPT MPI.")
    variant('mvapich2', default=False,
            description="Build mpi experiment collector for mvapich2 MPI.")
    variant('mvapich', default=False,
            description="Build mpi experiment collector for mvapich MPI.")
    variant('mpich2', default=False,
            description="Build mpi experiment collector for mpich2 MPI.")
    variant('mpich', default=False,
            description="Build mpi experiment collector for mpich MPI.")
    variant('runtime', default=False,
            description="build only the runtime libraries and collectors.")
    variant('build_type', default='None', values=('None'),
            description='CMake build type')
    variant('cti', default=False,
            description="Build MRNet with the CTI startup option")
    variant('crayfe', default=False,
            description="build only the FE tool using the runtime_dir \
                         to point to target build.")

    # Dependencies for cbtf-krell
    depends_on("cmake@3.0.2:", type='build')

    # For binutils service
    depends_on("binutils")

    # collectionTool
    depends_on("boost@1.50.0:")
    depends_on("dyninst@9.3.2:")
    depends_on("mrnet@5.0.1:+cti", when='+cti')
    depends_on("mrnet@5.0.1:+lwthreads")

    depends_on("xerces-c@3.1.1:")
    depends_on("cbtf")
    depends_on("cbtf+cti", when='+cti')
    depends_on("cbtf+runtime", when='+runtime')

    # for services and collectors
    depends_on("libmonitor+krellpatch")
    depends_on("libunwind")
    depends_on("papi")
    depends_on("llvm-openmp-ompt@tr6_forwards+standalone")

    # MPI Installations
    # These have not worked either for build or execution, commenting out for
    # now
    depends_on("openmpi", when='+openmpi')
    depends_on("mpich", when='+mpich')
    depends_on("mpich2", when='+mpich2')
    depends_on("mvapich2", when='+mvapich2')
    depends_on("mvapich", when='+mvapich')
    depends_on("mpt", when='+mpt')

    parallel = False

    build_directory = 'build_cbtf_krell'

    def set_RTOnly_cmakeOptions(self, spec, cmakeOptions):
        # Appends to cmakeOptions the options that will enable the appropriate
        # MPI implementations

        RTOnlyOptions = []
        RTOnlyOptions.append('-DRUNTIME_ONLY=true')
        cmakeOptions.extend(RTOnlyOptions)

    def set_mpi_cmakeOptions(self, spec, cmakeOptions):
        # Appends to cmakeOptions the options that will enable the appropriate
        # MPI implementations

        MPIOptions = []

        # openmpi
        if spec.satisfies('+openmpi'):
            MPIOptions.append('-DOPENMPI_DIR=%s' % spec['openmpi'].prefix)
        # mpich
        if spec.satisfies('+mpich'):
            MPIOptions.append('-DMPICH_DIR=%s' % spec['mpich'].prefix)
        # mpich2
        if spec.satisfies('+mpich2'):
            MPIOptions.append('-DMPICH2_DIR=%s' % spec['mpich2'].prefix)
        # mvapich
        if spec.satisfies('+mvapich'):
            MPIOptions.append('-DMVAPICH_DIR=%s' % spec['mvapich'].prefix)
        # mvapich2
        if spec.satisfies('+mvapich2'):
            MPIOptions.append('-DMVAPICH2_DIR=%s' % spec['mvapich2'].prefix)
        # mpt
        if spec.satisfies('+mpt'):
            MPIOptions.append('-DMPT_DIR=%s' % spec['mpt'].prefix)

        cmakeOptions.extend(MPIOptions)

    def set_CrayLoginNode_cmakeOptions(self, spec, cmakeOptions):
        # Appends to cmakeOptions the options that will enable
        # the appropriate Cray login node libraries

        CrayLoginNodeOptions = []
        rt_platform = "cray"
        # How do we get the compute node (CNL) cbtf package
        # install directory path. spec['cbtf'].prefix is the
        # login node path for this build, as we are building
        # the login node components with this spack invocation. We
        # need these paths to be the ones created in the CNL
        # spack invocation.
        be_cbtf = spack.store.db.query_one('cbtf arch=cray-CNL-haswell')
        be_cbtfk = spack.store.db.query_one('cbtf-krell arch=cray-CNL-haswell')
        be_papi = spack.store.db.query_one('papi arch=cray-CNL-haswell')
        be_boost = spack.store.db.query_one('boost arch=cray-CNL-haswell')
        be_mont = spack.store.db.query_one('libmonitor arch=cray-CNL-haswell')
        be_unw = spack.store.db.query_one('libunwind arch=cray-CNL-haswell')
        be_xer = spack.store.db.query_one('xerces-c arch=cray-CNL-haswell')
        be_dyn = spack.store.db.query_one('dyninst arch=cray-CNL-haswell')
        be_mrnet = spack.store.db.query_one('mrnet arch=cray-CNL-haswell')

        CrayLoginNodeOptions.append('-DCN_RUNTIME_PLATFORM=%s'
                                    % rt_platform)

        # Use install directories as CMAKE args for the building
        # of login cbtf-krell
        CrayLoginNodeOptions.append('-DCBTF_CN_RUNTIME_DIR=%s'
                                    % be_cbtf.prefix)
        CrayLoginNodeOptions.append('-DCBTF_KRELL_CN_RUNTIME_DIR=%s'
                                    % be_cbtfk.prefix)
        CrayLoginNodeOptions.append('-DPAPI_CN_RUNTIME_DIR=%s'
                                    % be_papi.prefix)
        CrayLoginNodeOptions.append('-DBOOST_CN_RUNTIME_DIR=%s'
                                    % be_boost.prefix)
        CrayLoginNodeOptions.append('-DLIBMONITOR_CN_RUNTIME_DIR=%s'
                                    % be_mont.prefix)
        CrayLoginNodeOptions.append('-DLIBUNWIND_CN_RUNTIME_DIR=%s'
                                    % be_unw.prefix)
        CrayLoginNodeOptions.append('-DXERCESC_CN_RUNTIME_DIR=%s'
                                    % be_xer.prefix)
        CrayLoginNodeOptions.append('-DDYNINST_CN_RUNTIME_DIR=%s'
                                    % be_dyn.prefix)
        CrayLoginNodeOptions.append('-DMRNET_CN_RUNTIME_DIR=%s'
                                    % be_mrnet.prefix)

        cmakeOptions.extend(CrayLoginNodeOptions)

    def cmake_args(self):
        spec = self.spec

        compile_flags = "-O2 -g"

        # Add in paths for finding package config files that tell us
        # where to find these packages
        cmake_args = [
            '-DCMAKE_CXX_FLAGS=%s'         % compile_flags,
            '-DCMAKE_C_FLAGS=%s'           % compile_flags,
            '-DCBTF_DIR=%s' % spec['cbtf'].prefix,
            '-DBINUTILS_DIR=%s' % spec['binutils'].prefix,
            '-DLIBMONITOR_DIR=%s' % spec['libmonitor'].prefix,
            '-DLIBUNWIND_DIR=%s' % spec['libunwind'].prefix,
            '-DPAPI_DIR=%s' % spec['papi'].prefix,
            '-DBOOST_DIR=%s' % spec['boost'].prefix,
            '-DMRNET_DIR=%s' % spec['mrnet'].prefix,
            '-DDYNINST_DIR=%s' % spec['dyninst'].prefix,
            '-DLIBIOMP_DIR=%s' % spec['llvm-openmp-ompt'].prefix,
            '-DXERCESC_DIR=%s' % spec['xerces-c'].prefix]

        if self.spec.satisfies('+runtime'):
            self.set_RTOnly_cmakeOptions(spec, cmake_args)

        # Add any MPI implementations coming from variant settings
        self.set_mpi_cmakeOptions(spec, cmake_args)

        if self.spec.satisfies('+crayfe'):
            # We need to build target/compute node components/libraries first
            # then pass those libraries to the cbtf-krell login node build
            self.set_CrayLoginNode_cmakeOptions(spec, cmake_args)

        return cmake_args
