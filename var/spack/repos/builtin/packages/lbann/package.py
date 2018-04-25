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
import os
import sys
from spack import *


class Lbann(CMakePackage):
    """LBANN: Livermore Big Artificial Neural Network Toolkit.  A distributed
    memory, HPC-optimized, model and data parallel training toolkit for deep
    neural networks."""

    homepage = "http://software.llnl.gov/lbann/"
    url      = "https://github.com/LLNL/lbann/archive/v0.91.tar.gz"

    version('develop', git='https://github.com/LLNL/lbann.git', branch="develop")
    version('0.93', '1913a25a53d4025fa04c16f14afdaa55')
    version('0.92', 'c0eb1595a7c74640e96f280beb497564')
    version('0.91', '83b0ec9cd0b7625d41dfb06d2abd4134')

    variant('gpu', default=False, description='Builds with support for GPUs via CUDA and cuDNN')
    variant('nccl', default=False, description='Builds with support for NCCL communication lib')
    variant('opencv', default=True, description='Builds with support for image processing routines with OpenCV')
    variant('seq_init', default=False, description='Force serial initialization of weight matrices.')
    variant('dtype', default='float',
            description='Type for floating point representation of weights',
            values=('float', 'double'))
    variant('build_type', default='Release',
            description='The build type to build',
            values=('Debug', 'Release'))

    depends_on('elemental +openmp_blas +shared +int64')
    depends_on('elemental +openmp_blas +shared +int64 build_type=Debug',
               when=('build_type=Debug'))
    depends_on('cuda', when='+gpu')
    depends_on('cudnn', when='+gpu')
    depends_on('cub', when='+gpu')
    depends_on('mpi')
    depends_on('hwloc ~pci ~libxml2')
    depends_on('opencv@3.2.0: +openmp +core +highgui +imgproc +jpeg +png +tiff +zlib ~eigen', when='+opencv')
    depends_on('protobuf@3.0.2:')
    depends_on('cnpy')
    depends_on('nccl', when='+gpu +nccl')

    @property
    def common_config_args(self):
        spec = self.spec
        # Environment variables
        CPPFLAGS = []
        CPPFLAGS.append('-DLBANN_SET_EL_RNG -ldl')

        return [
            '-DCMAKE_INSTALL_MESSAGE=LAZY',
            '-DCMAKE_CXX_FLAGS=%s' % ' '.join(CPPFLAGS),
            '-DLBANN_VERSION=spack',
            '-DCNPY_DIR={0}'.format(spec['cnpy'].prefix),
        ]

    # Get any recent versions or non-numeric version
    # Note that develop > numeric and non-develop < numeric
    @when('@:0.91' or '@0.94:')
    def cmake_args(self):
        spec = self.spec
        args = self.common_config_args
        args.extend([
            '-DLBANN_WITH_TOPO_AWARE:BOOL=%s' % ('+gpu +nccl' in spec),
            '-DLBANN_SEQUENTIAL_INITIALIZATION:BOOL=%s' %
            ('+seq_init' in spec),
            '-DLBANN_WITH_TBINF=OFF',
            '-DLBANN_WITH_VTUNE=OFF',
            '-DElemental_DIR={0}/CMake/elemental'.format(
                spec['elemental'].prefix),
            '-DLBANN_DATATYPE={0}'.format(spec.variants['dtype'].value),
            '-DLBANN_VERBOSE=0'])

        # Add support for OpenMP
        if (self.spec.satisfies('%clang')):
            if (sys.platform == 'darwin'):
                clang = self.compiler.cc
                clang_bin = os.path.dirname(clang)
                clang_root = os.path.dirname(clang_bin)
                args.extend([
                    '-DOpenMP_CXX_FLAGS=-fopenmp=libomp',
                    '-DOpenMP_CXX_LIB_NAMES=libomp',
                    '-DOpenMP_libomp_LIBRARY={0}/lib/libomp.dylib'.format(
                        clang_root)])

        if '+opencv' in spec:
            args.extend(['-DOpenCV_DIR:STRING={0}'.format(
                spec['opencv'].prefix)])

        if '+gpu' in spec:
            args.extend([
                '-DLBANN_WITH_CUDA:BOOL=%s' % ('+gpu' in spec),
                '-DLBANN_WITH_SOFTMAX_CUDA:BOOL=%s' % ('+gpu' in spec),
                '-DCUDA_TOOLKIT_ROOT_DIR={0}'.format(
                    spec['cuda'].prefix)])
            args.extend([
                '-DLBANN_WITH_CUDNN:BOOL=%s' % ('+gpu' in spec),
                '-DcuDNN_DIR={0}'.format(
                    spec['cudnn'].prefix)])
            args.extend(['-DCUB_DIR={0}'.format(
                spec['cub'].prefix)])
            if '+nccl' in spec:
                args.extend([
                    '-DLBANN_WITH_NCCL:BOOL=%s' % ('+gpu +nccl' in spec),
                    '-DNCCL_DIR={0}'.format(
                        spec['nccl'].prefix)])

        return args

    @when('@0.91:0.93')
    def cmake_args(self):
        spec = self.spec
        args = self.common_config_args
        args.extend([
            '-DWITH_CUDA:BOOL=%s' % ('+gpu' in spec),
            '-DWITH_CUDNN:BOOL=%s' % ('+gpu' in spec),
            '-DELEMENTAL_USE_CUBLAS:BOOL=%s' % (
                '+cublas' in spec['elemental']),
            '-DWITH_TBINF=OFF',
            '-DWITH_VTUNE=OFF',
            '-DElemental_DIR={0}'.format(spec['elemental'].prefix),
            '-DELEMENTAL_MATH_LIBS={0}'.format(
                spec['elemental'].libs),
            '-DSEQ_INIT:BOOL=%s' % ('+seq_init' in spec),
            '-DVERBOSE=0',
            '-DLBANN_HOME=.'])

        if spec.variants['dtype'].value == 'float':
            args.extend(['-DDATATYPE=4'])
        elif spec.variants['dtype'].value == 'double':
            args.extend(['-DDATATYPE=8'])

        if '+opencv' in spec:
            args.extend(['-DOpenCV_DIR:STRING={0}'.format(
                spec['opencv'].prefix)])

        if '+cudnn' in spec:
            args.extend(['-DcuDNN_DIR={0}'.format(
                spec['cudnn'].prefix)])

        if '+cub' in spec:
            args.extend(['-DCUB_DIR={0}'.format(
                spec['cub'].prefix)])

        return args
