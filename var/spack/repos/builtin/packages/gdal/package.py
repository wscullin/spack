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
import sys


class Gdal(AutotoolsPackage):
    """GDAL is a translator library for raster and vector geospatial
    data formats that is released under an X/MIT style Open Source
    license by the Open Source Geospatial Foundation. As a library,
    it presents a single raster abstract data model and vector
    abstract data model to the calling application for all supported
    formats. It also comes with a variety of useful command line
    utilities for data translation and processing.
    """

    homepage   = "http://www.gdal.org/"
    url        = "http://download.osgeo.org/gdal/2.1.2/gdal-2.1.2.tar.xz"
    list_url   = "http://download.osgeo.org/gdal/"
    list_depth = 1

    version('2.1.2', 'ae85b78888514c75e813d658cac9478e')
    version('2.0.2', '940208e737c87d31a90eaae43d0efd65')

    extends('python')

    variant('hdf5', default=False, description='Enable HDF5 support')
    variant('hdf', default=False, description='Enable HDF4 support')
    variant('openjpeg', default=False, description='Enable JPEG2000 support')
    variant('geos', default=False, description='Enable GEOS support')
    variant('kea', default=False, description='Enable KEA support')
    variant('netcdf', default=False, description='Enable netcdf support')

    depends_on('swig')
    depends_on("hdf5", when='+hdf5')
    depends_on("hdf", when='+hdf')
    depends_on("openjpeg", when='+openjpeg')
    depends_on("geos", when='+geos')
    depends_on("kealib", when='+kea')
    depends_on("netcdf", when='+netcdf')
    depends_on("libtiff")
    depends_on("libpng")
    depends_on("zlib")
    depends_on("proj")
    depends_on("py-numpy", type=('build', 'run'))

    parallel = False

    def configure_args(self):
        spec = self.spec

        args = []
        args.append("--with-liblzma=yes")
        args.append("--with-zlib=%s" % spec['zlib'].prefix)
        args.append("--with-python=%s" % spec['python'].command.path)
        args.append("--without-libtool")

        if '+geos' in spec:
            args.append('--with-geos=yes')
        if '+hdf' in spec:
            args.append('--with-hdf4=%s' % spec['hdf'].prefix)
        if '+hdf5' in spec:
            args.append('--with-hdf5=%s' % spec['hdf5'].prefix)
        if '+openjpeg' in spec:
            args.append('--with-openjpeg=%s' % spec['openjpeg'].prefix)
        if '+kea' in spec:
            args.append('--with-kea=yes')
        if '+netcdf' in spec:
            args.append('--with-netcdf=%s' % spec['netcdf'].prefix)

        return args

    @run_after('install')
    def darwin_fix(self):
        # The shared library is not installed correctly on Darwin; fix this
        if sys.platform == 'darwin':
            fix_darwin_install_name(self.prefix.lib)
