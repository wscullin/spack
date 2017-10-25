##############################################################################
# Copyright (c) 2013-2017, Lawrence Livermore National Security, LLC.
# Produced at the Lawrence Livermore National Laboratory.
#
# This file is part of Spack.
# Created by Todd Gamblin, tgamblin@llnl.gov, All rights reserved.
# LLNL-CODE-647188
#
# For details, see https://github.com/llnl/spack
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


class Htslib(AutotoolsPackage):
    """C library for high-throughput sequencing data formats."""

    homepage = "https://github.com/samtools/htslib"
    url      = "https://github.com/samtools/htslib/releases/download/1.3.1/htslib-1.3.1.tar.bz2"

    version('1.6', 'd6fd14e208aca7e08cbe9072233d0af9')
    version('1.4', '2a22ff382654c033c40e4ec3ea880050')
    version('1.3.1', '16d78f90b72f29971b042e8da8be6843')
    version('1.2', '64026d659c3b062cfb6ddc8a38e9779f',
      url='https://github.com/samtools/htslib/archive/1.2.tar.gz')

    depends_on('zlib')
    depends_on('bzip2', when="@1.4:")
    depends_on('xz', when="@1.4:")

    depends_on('m4', when="@1.2")
    depends_on('autoconf', when="@1.2")
    depends_on('automake', when="@1.2")
    depends_on('libtool', when="@1.2")
