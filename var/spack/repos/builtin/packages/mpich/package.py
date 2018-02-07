##############################################################################
# Copyright (c) 2013-2017, Lawrence Livermore National Security, LLC.
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
from spack import *
import os


class Mpich(AutotoolsPackage):
    """MPICH is a high performance and widely portable implementation of
    the Message Passing Interface (MPI) standard."""

    homepage = "http://www.mpich.org"
    url = "http://www.mpich.org/static/downloads/3.0.4/mpich-3.0.4.tar.gz"
    list_url = "http://www.mpich.org/static/downloads/"
    list_depth = 1

    version('3.2',   'f414cfa77099cd1fa1a5ae4e22db508a')
    version('3.1.4', '2ab544607986486562e076b83937bba2')
    version('3.1.3', '93cb17f91ac758cbf9174ecb03563778')
    version('3.1.2', '7fbf4b81dcb74b07ae85939d1ceee7f1')
    version('3.1.1', '40dc408b1e03cc36d80209baaa2d32b7')
    version('3.1',   '5643dd176499bfb7d25079aaff25f2ec')
    version('3.0.4', '9c5d5d4fe1e17dd12153f40bc5b6dbc0')
    version('develop', git='git://github.com/pmodels/mpich')

    variant('hydra', default=True,  description='Build the hydra process manager')
    variant('pmi',   default=True,  description='Build with PMI support')
    variant('romio', default=True,  description='Enable ROMIO MPI I/O implementation')
    variant('verbs', default=False, description='Build support for OpenFabrics verbs.')
    variant(
        'device',
        default='ch3',
        description='''Abstract Device Interface (ADI)
implementation. The ch4 device is currently in experimental state''',
        values=('ch3', 'ch4'),
        multi=False
    )
    variant(
        'netmod',
        default='tcp',
        description='''Network module. Only single netmod builds are
supported. For ch3 device configurations, this presumes the
ch3:nemesis communication channel. ch3:sock is not supported by this
spack package at this time.''',
        values=('tcp', 'mxm', 'ofi', 'ucx'),
        multi=False
    )

    provides('mpi')
    provides('mpi@:3.0', when='@3:')
    provides('mpi@:1.3', when='@1:')

    # fix MPI_Barrier segmentation fault
    # see https://lists.mpich.org/pipermail/discuss/2016-May/004764.html
    # and https://lists.mpich.org/pipermail/discuss/2016-June/004768.html
    patch('mpich32_clang.patch', when='@3.2%clang')

    depends_on('libfabric', when='netmod=ofi')

    conflicts('device=ch4', when='@:3.2')
    conflicts('netmod=ofi', when='@:3.1.4')
    conflicts('netmod=ucx', when='device=ch3')
    conflicts('netmod=mxm', when='device=ch4')
    conflicts('netmod=mxm', when='@:3.1.3')
    conflicts('netmod=tcp', when='device=ch4')

    def setup_dependent_environment(self, spack_env, run_env, dependent_spec):
        # On Cray, the regular compiler wrappers *are* the MPI wrappers.
        if 'platform=cray' in self.spec:
            spack_env.set('MPICC',  spack_cc)
            spack_env.set('MPICXX', spack_cxx)
            spack_env.set('MPIF77', spack_fc)
            spack_env.set('MPIF90', spack_fc)
        else:
            spack_env.set('MPICC',  join_path(self.prefix.bin, 'mpicc'))
            spack_env.set('MPICXX', join_path(self.prefix.bin, 'mpic++'))
            spack_env.set('MPIF77', join_path(self.prefix.bin, 'mpif77'))
            spack_env.set('MPIF90', join_path(self.prefix.bin, 'mpif90'))

        spack_env.set('MPICH_CC', spack_cc)
        spack_env.set('MPICH_CXX', spack_cxx)
        spack_env.set('MPICH_F77', spack_f77)
        spack_env.set('MPICH_F90', spack_fc)
        spack_env.set('MPICH_FC', spack_fc)

    def setup_dependent_package(self, module, dependent_spec):
        if 'platform=cray' in self.spec:
            self.spec.mpicc = spack_cc
            self.spec.mpicxx = spack_cxx
            self.spec.mpifc = spack_fc
            self.spec.mpif77 = spack_f77
        else:
            self.spec.mpicc = join_path(self.prefix.bin, 'mpicc')
            self.spec.mpicxx = join_path(self.prefix.bin, 'mpic++')
            self.spec.mpifc = join_path(self.prefix.bin, 'mpif90')
            self.spec.mpif77 = join_path(self.prefix.bin, 'mpif77')

        self.spec.mpicxx_shared_libs = [
            join_path(self.prefix.lib, 'libmpicxx.{0}'.format(dso_suffix)),
            join_path(self.prefix.lib, 'libmpi.{0}'.format(dso_suffix))
        ]

    def autoreconf(self, spec, prefix):
        """Not needed usually, configure should be already there"""
        # If configure exists nothing needs to be done
        if os.path.exists(self.configure_abs_path):
            return
        # Else bootstrap with autotools
        bash = which('bash')
        bash('./autogen.sh')

    @run_before('autoreconf')
    def die_without_fortran(self):
        # Until we can pass variants such as +fortran through virtual
        # dependencies depends_on('mpi'), require Fortran compiler to
        # avoid delayed build errors in dependents.
        if (self.compiler.f77 is None) or (self.compiler.fc is None):
            raise InstallError(
                'Mpich requires both C and Fortran compilers!'
            )

    def configure_args(self):
        spec = self.spec
        config_args = [
            '--enable-shared',
            '--with-pm={0}'.format('hydra' if '+hydra' in spec else 'no'),
            '--with-pmi={0}'.format('yes' if '+pmi' in spec else 'no'),
            '--{0}-romio'.format('enable' if '+romio' in spec else 'disable'),
            '--{0}-ibverbs'.format('with' if '+verbs' in spec else 'without')
        ]

        # setup device configuration
        device_config = ''
        if 'device=ch4' in spec:
            device_config = '--with-device=ch4:'
        elif 'device=ch3' in spec:
            device_config = '--with-device=ch3:nemesis:'

        if 'netmod=ucx' in spec:
            device_config += 'ucx'
        elif 'netmod=ofi' in spec:
            device_config += 'ofi'
        elif 'netmod=mxm' in spec:
            device_config += 'mxm'
        elif 'netmod=tcp' in spec:
            device_config += 'tcp'

        config_args.append(device_config)

        return config_args

    @run_after('install')
    def filter_compilers(self):
        """Run after install to make the MPI compilers use the
        compilers that Spack built the package with.

        If this isn't done, they'll have CC, CXX, F77, and FC set
        to Spack's generic cc, c++, f77, and f90.  We want them to
        be bound to whatever compiler they were built with."""

        mpicc = join_path(self.prefix.bin, 'mpicc')
        mpicxx = join_path(self.prefix.bin, 'mpicxx')
        mpif77 = join_path(self.prefix.bin, 'mpif77')
        mpif90 = join_path(self.prefix.bin, 'mpif90')

        # Substitute Spack compile wrappers for the real
        # underlying compiler
        kwargs = {
            'ignore_absent': True,
            'backup': False,
            'string': True
        }
        filter_file(env['CC'],  self.compiler.cc,  mpicc,  **kwargs)
        filter_file(env['CXX'], self.compiler.cxx, mpicxx, **kwargs)
        filter_file(env['F77'], self.compiler.f77, mpif77, **kwargs)
        filter_file(env['FC'],  self.compiler.fc,  mpif90, **kwargs)

        # Remove this linking flag if present
        # (it turns RPATH into RUNPATH)
        for wrapper in (mpicc, mpicxx, mpif77, mpif90):
            filter_file('-Wl,--enable-new-dtags', '', wrapper, **kwargs)
