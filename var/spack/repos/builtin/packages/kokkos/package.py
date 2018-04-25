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
from spack import *


class Kokkos(Package):
    """Kokkos implements a programming model in C++ for writing performance
    portable applications targeting all major HPC platforms."""

    homepage = "https://github.com/kokkos/kokkos"
    url      = "https://github.com/kokkos/kokkos/archive/2.03.00.tar.gz"

    version('2.5.00',  '2db83c56587cb83b772d0c81a3228a21')
    version('2.04.11', 'd4849cee6eb9001d61c30f1d9fe74336')
    version('2.04.04', '2c6d1c2569b91c9fcd4117296438e65c')
    version('2.04.00', 'd99ac790ff5f29545d8eb53de90c0a85')
    version('2.03.13', '3874a159a517384541ea5b52f85501ba')
    version('2.03.05', '8727d783453f719eec392e10a36b49fd')
    version('2.03.00', 'f205d659d4304747759fabfba32d43c3')
    version('2.02.15', 'de41e38f452a50bb03363c519fe20769')
    version('2.02.07', 'd5baeea70109249f7dca763074ffb202')
    version('develop', git='https://github.com/kokkos/kokkos',
            branch='develop')

    variant('qthreads', default=False, description="enable Qthreads backend")
    variant('cuda', default=False, description="enable Cuda backend")
    variant('openmp', default=True, description="enable OpenMP backend")

    # Specify that v1.x is required as v2.x has API changes
    depends_on('hwloc@:1')
    depends_on('qthreads', when='+qthreads')
    depends_on('cuda', when='+cuda')

    def install(self, spec, prefix):
        generate = which(join_path(self.stage.source_path,
                                   'generate_makefile.bash'))
        with working_dir('build', create=True):
            g_args = [
                '--prefix=%s' % prefix,
                '--with-hwloc=%s' % spec['hwloc'].prefix,
                '--with-serial'
            ]
            if '+openmp' in spec:
                g_args.append('--with-openmp')
            if 'qthreads' in spec:
                g_args.append('--with-qthreads=%s' % spec['qthreads'].prefix)
            if 'cuda' in spec:
                g_args.append('--with-cuda=%s' % spec['cuda'].prefix)

            generate(*g_args)
            make()
            make('install')
