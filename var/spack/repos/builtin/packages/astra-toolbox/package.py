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
import sys

class AstraToolbox(Package):
    """The ASTRA Toolbox is a MATLAB and Python toolbox of high-performance
       GPU primitives for 2D and 3D tomography."""

    homepage = "http://www.astra-toolbox.com/"
    url      = "https://github.com/astra-toolbox/astra-toolbox/archive/v1.8.tar.gz"

    version('1.8',   '1cd8857cfbc83a60d573a86b0be63d82')
    version('1.7.1', 'd0671c7e760b1f00bb2fc18f224b0f82')
    version('1.7',   'f4005f9304fed47b8423039a9131c83c')

    variant('cuda', default=False, description='Build with CUDA support')
    variant('python', default=True, description='Provide support for python')
    variant('matlab', default=False, description='Provide support for matlab')

    depends_on('cuda', when='+cuda')
    depends_on('python', when='+python')
    depends_on('py-cython', when='+python')
    depends_on('py-numpy', when='+python')
    depends_on('py-scipy', when='+python')
    depends_on('py-six', when='+python')
    depends_on('matlab', when='+matlab')
    depends_on('boost')
   
    extends('python', when='+python')
    
    extends('matlab', when='+matlab') 

    def patch(self):
        """Defeat the installer to install into a default location such
        that PYTHONPATH need not be set"""
        filter_file(r'build install$',
                    r'build install --prefix=@prefix@',
                    'build/linux/Makefile.in')

    def configure_args(self):

        spec = self.spec

        args = ['--with-install-type=module']
        args.append('--prefix={0}'.format(self.prefix))
        args.append('--with-boost={0}'.format(spec['boost'].prefix))
        if self.spec.satisfies('+cuda'):
            args.append('--with-cuda={0}'.format(spec['cuda'].prefix))
        if self.spec.satisfies('+python'):
            args.append('--with-python={0}'.format(spec['python'].command.path))
        if self.spec.satisfies('+matlab'):
            args.append('--with-matlab={0}'.format(spec['matlab'].prefix))
            
        return args

    def autoreconf(self, spec, prefix):
            bash = which('bash')
            bash('./autogen.sh')

    def configure(self, spec, prefix):
            configure(*self.configure_args())

    def install(self, spec, prefix):
        with working_dir('build'):
            with working_dir('linux'):
                self.autoreconf(spec, prefix)
                self.configure(spec, prefix)
                make()
                make("install")

