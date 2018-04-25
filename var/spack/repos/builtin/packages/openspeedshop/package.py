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
##############################################################################
# Copyright (c) 2015-2018 Krell Institute. All Rights Reserved.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA  02111-1307  USA
##############################################################################

from spack import *

import spack
import spack.store

import os
import os.path


class Openspeedshop(CMakePackage):
    """OpenSpeedShop is a community effort by The Krell Institute with
       current direct funding from DOEs NNSA.  It builds on top of a
       broad list of community infrastructures, most notably Dyninst
       and MRNet from UW, libmonitor from Rice, and PAPI from UTK.
       OpenSpeedShop is an open source multi platform Linux performance
       tool which is targeted to support performance analysis of
       applications running on both single node and large scale IA64,
       IA32, EM64T, AMD64, PPC, ARM, Power8, Intel Phi, Blue Gene and
       Cray platforms.  OpenSpeedShop development is hosted by the Krell
       Institute. The infrastructure and base components of OpenSpeedShop
       are released as open source code primarily under LGPL.
    """

    homepage = "http://www.openspeedshop.org"
    url = "https://github.com/OpenSpeedShop"

    # Use when the git repository is available
    version('2.3.1', branch='master',
            git='https://github.com/OpenSpeedShop/openspeedshop.git')

    variant('offline', default=False,
            description="build with offline instrumentor enabled.")
    variant('cbtf', default=True,
            description="build with cbtf instrumentor enabled.")
    variant('runtime', default=False,
            description="build only the runtime libraries and collectors.")
    variant('cti', default=False,
            description="Build MRNet with the CTI startup option")
    variant('crayfe', default=False,
            description="build only the FE tool using the runtime_dir \
                         to point to target build.")
    variant('cuda', default=False,
            description="build with cuda packages included.")

    variant('gui', default='qt3', values=('none', 'qt3', 'qt4'),
            description='Build or not build a GUI of choice'
    )

    variant('build_type', default='None', values=('None'),
            description='CMake build type')

    # MPI variants
    variant('openmpi', default=False,
            description="Build mpi collector for openmpi \
                         MPI when variant is enabled.")
    variant('mpt', default=False,
            description="Build mpi collector for SGI \
                         MPT MPI when variant is enabled.")
    variant('mvapich2', default=False,
            description="Build mpi collector for mvapich2\
                         MPI when variant is enabled.")
    variant('mvapich', default=False,
            description="Build mpi collector for mvapich\
                         MPI when variant is enabled.")
    variant('mpich2', default=False,
            description="Build mpi collector for mpich2\
                         MPI when variant is enabled.")
    variant('mpich', default=False,
            description="Build mpi collector for mpich\
                         MPI when variant is enabled.")

    depends_on("cmake@3.0.2:", type='build')
    # Dependencies for openspeedshop that are common to all
    # the variants of the OpenSpeedShop build
    depends_on("libtool", type='build')
    depends_on("bison", type='build')
    depends_on("flex", type='build')
    depends_on("binutils", type='build')
    depends_on("elf", type="link")
    depends_on("libdwarf")
    depends_on("sqlite")
    depends_on("boost@1.50.0:")
    depends_on("dyninst@9.3.2:")
    depends_on("python")
    depends_on("libxml2+python")
    depends_on("qt@3.3.8b+krellpatch", when='gui=qt3')
    # Actively working on adding this gui package
    # depends_on("cbtf-argonavis-gui", when='gui=qt4')

    # Dependencies only for the openspeedshop offline package.
    depends_on("libunwind", when='+offline')
    depends_on("papi", when='+offline')
    depends_on("libmonitor+krellpatch", when='+offline')
    depends_on("openmpi", when='+offline+openmpi')
    depends_on("mpich", when='+offline+mpich')
    depends_on("mpich2", when='+offline+mpich2')
    depends_on("mvapich2", when='+offline+mvapich2')
    depends_on("mvapich", when='+offline+mvapich')
    depends_on("mpt", when='+offline+mpt')

    # Dependencies only for the openspeedshop cbtf package.
    depends_on("cbtf", when='+cbtf')
    depends_on('cbtf-krell', when='+cbtf')
    depends_on('cbtf-krell+crayfe', when='+crayfe')
    depends_on('cbtf-krell+cti', when='+cti')
    depends_on('cbtf-krell+mpich', when='+cbtf+mpich')
    depends_on('cbtf-krell+mpich2', when='+cbtf+mpich2')
    depends_on('cbtf-krell+mpt', when='+cbtf+mpt')
    depends_on('cbtf-krell+mvapich', when='+cbtf+mvapich')
    depends_on('cbtf-krell+mvapich2', when='+cbtf+mvapich2')
    depends_on('cbtf-krell+openmpi', when='+cbtf+openmpi')
    depends_on("cbtf-argonavis", when='+cbtf+cuda')
    depends_on("mrnet@5.0.1:+lwthreads", when='+cbtf')
    depends_on("mrnet@5.0.1:+cti", when='+cti+cbtf')

    parallel = False

    build_directory = 'build_openspeedshop'

    def set_CrayLoginNode_cmakeOptions(self, spec, cmakeOptions):
        # Appends to cmakeOptions the options that will enable the appropriate
        # Cray login node libraries

        CrayLoginNodeOptions = []
        rt_platform = "cray"
        # How do we get the compute node (CNL) cbtf package install
        # directory path?
        # spec['cbtf'].prefix is the login node value for this build, as
        # we only get here when building the login node components and
        # that is all that is known to spack.
        be_ck = spack.store.db.query_one('cbtf-krell arch=cray-CNL-haswell')

        # Equivalent to install-tool cmake arg:
        # '-DCBTF_KRELL_CN_RUNTIME_DIR=%s'
        #               % <base dir>/cbtf_v2.3.1.release/compute)
        CrayLoginNodeOptions.append('-DCBTF_KRELL_CN_RUNTIME_DIR=%s'
                                    % be_ck.prefix)
        CrayLoginNodeOptions.append('-DRUNTIME_PLATFORM=%s'
                                    % rt_platform)

        cmakeOptions.extend(CrayLoginNodeOptions)

    def cmake_args(self):

        spec = self.spec

        compile_flags = "-O2 -g"

        if spec.satisfies('+offline'):
            # Indicate building offline vers (writes rawdata files)
            instrumentor_setting = "offline"
            if spec.satisfies('+runtime'):
                cmake_args = [
                    '-DCMAKE_CXX_FLAGS=%s'  % compile_flags,
                    '-DCMAKE_C_FLAGS=%s'    % compile_flags,
                    '-DINSTRUMENTOR=%s'     % instrumentor_setting,
                    '-DLIBMONITOR_DIR=%s'   % spec['libmonitor'].prefix,
                    '-DLIBUNWIND_DIR=%s'    % spec['libunwind'].prefix,
                    '-DPAPI_DIR=%s'         % spec['papi'].prefix]

                # Add any MPI implementations coming from variant settings
                self.set_mpi_cmakeOptions(spec, cmake_args)

            else:
                cmake_args = []

                # Appends base options to cmake_args
                self.set_defaultbase_cmakeOptions(spec, cmake_args)
                cmake_args.extend(
                    ['-DCMAKE_CXX_FLAGS=%s'  % compile_flags,
                     '-DCMAKE_C_FLAGS=%s'    % compile_flags,
                     '-DINSTRUMENTOR=%s' % instrumentor_setting,
                     '-DLIBMONITOR_DIR=%s' % spec['libmonitor'].prefix,
                     '-DLIBUNWIND_DIR=%s' % spec['libunwind'].prefix,
                     '-DPAPI_DIR=%s' % spec['papi'].prefix,
                     '-DSQLITE3_DIR=%s' % spec['sqlite'].prefix,
                     '-DQTLIB_DIR=%s' % spec['qt'].prefix])

                # Add any MPI implementations coming from variant settings
                self.set_mpi_cmakeOptions(spec, cmake_args)

        elif spec.satisfies('+cbtf'):

            cmake_args = []

            # Indicate building cbtf vers (transfer rawdata files)
            instrumentor_setting = "cbtf"

            if spec.satisfies('+runtime'):
                # Appends base options to cmake_args
                self.set_defaultbase_cmakeOptions(spec, cmake_args)

                cmake_args.extend(
                    ['-DCMAKE_CXX_FLAGS=%s'  % compile_flags,
                     '-DCMAKE_C_FLAGS=%s'    % compile_flags,
                     '-DINSTRUMENTOR=%s' % instrumentor_setting,
                     '-DCBTF_DIR=%s' % spec['cbtf'].prefix,
                     '-DCBTF_KRELL_DIR=%s' % spec['cbtf-krell'].prefix,
                     '-DMRNET_DIR=%s' % spec['mrnet'].prefix])

            else:

                # Appends base options to cmake_args
                self.set_defaultbase_cmakeOptions(spec, cmake_args)
                guitype = self.spec.variants['gui'].value
                cmake_args.extend(
                    ['-DCMAKE_CXX_FLAGS=%s' % compile_flags,
                     '-DCMAKE_C_FLAGS=%s' % compile_flags,
                     '-DINSTRUMENTOR=%s' % instrumentor_setting,
                     '-DSQLITE3_DIR=%s' % spec['sqlite'].prefix,
                     '-DCBTF_DIR=%s' % spec['cbtf'].prefix,
                     '-DCBTF_KRELL_DIR=%s' % spec['cbtf-krell'].prefix,
                     '-DMRNET_DIR=%s' % spec['mrnet'].prefix])

                if guitype == 'none':
                    cmake_args.extend(
                        ['-DBUILD_QT3_GUI=FALSE'])
                elif guitype == 'qt4':
                    cmake_args.extend(
                        ['-DBUILD_QT3_GUI=FALSE'])
                elif guitype == 'qt3':
                    cmake_args.extend(
                        ['-DQTLIB_DIR=%s'
                            % spec['qt'].prefix])

                if spec.satisfies('+crayfe'):
                    # We need to build target/compute node
                    # components/libraries first then pass
                    # those libraries to the openspeedshop
                    # login node build
                    self.set_CrayLoginNode_cmakeOptions(spec, cmake_args)

        return cmake_args

    def set_defaultbase_cmakeOptions(self, spec, cmakeOptions):
        # Appends to cmakeOptions the options that will enable
        # the appropriate base level options to the openspeedshop
        # cmake build.
        python_exe = spec['python'].command.path
        python_library = spec['python'].libs[0]
        python_include = spec['python'].headers.directories[0]

        BaseOptions = []

        BaseOptions.append('-DBINUTILS_DIR=%s' % spec['binutils'].prefix)
        BaseOptions.append('-DLIBELF_DIR=%s' % spec['elf'].prefix)
        BaseOptions.append('-DLIBDWARF_DIR=%s' % spec['libdwarf'].prefix)
        BaseOptions.append('-DPYTHON_EXECUTABLE=%s' % python_exe)
        BaseOptions.append('-DPYTHON_INCLUDE_DIR=%s' % python_include)
        BaseOptions.append('-DPYTHON_LIBRARY=%s' % python_library)
        BaseOptions.append('-DBoost_NO_SYSTEM_PATHS=TRUE')
        BaseOptions.append('-DBoost_NO_BOOST_CMAKE=TRUE')
        BaseOptions.append('-DBOOST_ROOT=%s' % spec['boost'].prefix)
        BaseOptions.append('-DBoost_DIR=%s' % spec['boost'].prefix)
        BaseOptions.append('-DBOOST_LIBRARYDIR=%s' % spec['boost'].prefix.lib)
        BaseOptions.append('-DDYNINST_DIR=%s' % spec['dyninst'].prefix)

        cmakeOptions.extend(BaseOptions)

    def set_mpi_cmakeOptions(self, spec, cmakeOptions):
        # Appends to cmakeOptions the options that will enable
        # the appropriate MPI implementations

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

    def setup_environment(self, spack_env, run_env):
        """Set up the compile and runtime environments for a package."""

        # Common settings to both offline and cbtf versions
        # of OpenSpeedShop
        run_env.prepend_path('PATH', self.prefix.bin)

        # Find Dyninst library path, this is needed to
        # set the DYNINSTAPI_RT_LIB library which is
        # required for OpenSpeedShop to find loop level
        # performance information
        dyninst_libdir = find_libraries('libdyninstAPI_RT',
                                        root=self.spec['dyninst'].prefix,
                                        shared=True, recursive=True)

        # Set Dyninst RT library path to support OSS loop resolution code
        run_env.set('DYNINSTAPI_RT_LIB', dyninst_libdir)

        # Find openspeedshop library path
        oss_libdir = find_libraries('libopenss-framework',
                                    root=self.spec['openspeedshop'].prefix,
                                    shared=True, recursive=True)
        run_env.prepend_path('LD_LIBRARY_PATH',
                             os.path.dirname(oss_libdir.joined()))

        run_env.set('OPENSS_RAWDATA_DIR', '.')
        # Settings specific to the version, checking here
        # for the offline instrumentor, otherwise use cbtf instrumentor
        # settings. MPI for the cbtf instrumentor is setup in cbtf-krell
        if '+offline' in self.spec:
            # Had to use this form of syntax self.prefix.lib and
            # self.prefix.lib64 returned None all the time
            run_env.set('OPENSS_PLUGIN_PATH',
                        join_path(oss_libdir + '/openspeedshop'))
            run_env.prepend_path('PATH', self.spec['papi'].prefix.bin)
            run_env.prepend_path('PATH', self.spec['libdwarf'].prefix.bin)
            run_env.prepend_path('PATH', self.spec['python'].prefix.bin)

            if '+mpich' in self.spec:
                run_env.set('OPENSS_MPI_IMPLEMENTATION', 'mpich')
            if '+mpich2' in self.spec:
                run_env.set('OPENSS_MPI_IMPLEMENTATION', 'mpich2')
            if '+mvapich2' in self.spec:
                run_env.set('OPENSS_MPI_IMPLEMENTATION', 'mvapich2')
            if '+openmpi' in self.spec:
                run_env.set('OPENSS_MPI_IMPLEMENTATION', 'openmpi')
        else:
            cbtf_mc = '/sbin/cbtf_mrnet_commnode'
            cbtf_lmb = '/sbin/cbtf_libcbtf_mrnet_backend'
            run_env.set('XPLAT_RSH', 'ssh')
            run_env.set('MRNET_COMM_PATH',
                        join_path(self.spec['cbtf-krell'].prefix + cbtf_mc))
            run_env.set('CBTF_MRNET_BACKEND_PATH',
                        join_path(self.spec['cbtf-krell'].prefix + cbtf_lmb))
            run_env.prepend_path('PATH', self.spec['mrnet'].prefix.bin)
            run_env.prepend_path('PATH', self.spec['cbtf-krell'].prefix.bin)
            run_env.prepend_path('PATH', self.spec['cbtf-krell'].prefix.sbin)
            run_env.prepend_path('PATH', self.spec['python'].prefix.bin)
