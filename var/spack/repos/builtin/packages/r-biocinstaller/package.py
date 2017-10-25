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


class RBiocinstaller(RPackage):
    """This package is used to install and update Bioconductor, CRAN,
    and (some) github packages."""

    homepage = "https://bioconductor.org/packages/BiocInstaller/"
    url      = "https://bioconductor.org/packages/3.5/bioc/src/contrib/BiocInstaller_1.26.1.tar.gz"
    list_url = homepage

    version('1.26.1', 'ec0f8866639475bcd91179dcc840b5f4')
    version('1.25.3', '6214770455a5122dca5544861f52c91d')

    depends_on('r@3.4.0:3.4.9', when='@1.26.1')
