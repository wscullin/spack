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


class RSummarizedexperiment(RPackage):
    """The SummarizedExperiment container contains one or more assays, each
       represented by a matrix-like object of numeric or other mode. The rows
       typically represent genomic ranges of interest and the columns
       represent samples."""

    homepage = "https://bioconductor.org/packages/SummarizedExperiment/"
    url      = "https://bioconductor.org/packages/3.5/bioc/src/contrib/SummarizedExperiment_1.6.5.tar.gz"
    list_url = homepage

    version('1.6.5', '8f7d534e37cfda1e3e145ec7609c61f5')

    depends_on('r-genomicranges', type=('build', 'run'))
    depends_on('r-biobase', type=('build', 'run'))
    depends_on('r-delayedarray', type=('build', 'run'))
    depends_on('r-matrix', type=('build', 'run'))
    depends_on('r-s4vectors', type=('build', 'run'))
    depends_on('r-iranges', type=('build', 'run'))
    depends_on('r-genomeinfodb', type=('build', 'run'))
    depends_on('r@3.4.0:3.4.9', when='@1.6.5')
