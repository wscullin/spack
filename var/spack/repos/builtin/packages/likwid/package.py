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
import glob


class Likwid(Package):
    """Likwid is a simple to install and use toolsuite of command line
    applications for performance oriented programmers. It works for Intel and
    AMD processors on the Linux operating system."""

    homepage = "https://github.com/RRZE-HPC/likwid"
    url      = "https://github.com/RRZE-HPC/likwid/archive/4.1.2.tar.gz"

    maintainers = ['davydden']

    version('4.1.2', 'a857ce5bd23e31d96e2963fe81cb38f0')

    # NOTE: There is no way to use an externally provided hwloc with Likwid.
    # The reason is that the internal hwloc is patched to contain extra
    # functionality and functions are prefixed with "likwid_".

    # TODO: how to specify those?
    # depends_on('lua')

    # TODO: check
    # depends_on('gnuplot', type='run')

    depends_on('perl', type=('build', 'run'))

    supported_compilers = {'clang': 'CLANG', 'gcc': 'GCC', 'intel': 'ICC'}

    def patch(self):
        files = glob.glob('perl/*.*') + glob.glob('bench/perl/*.*')

        # Allow the scripts to find Spack's perl
        filter_file('^#!/usr/bin/perl -w', '#!/usr/bin/env perl', *files)
        filter_file('^#!/usr/bin/perl', '#!/usr/bin/env perl', *files)

    @run_before('install')
    def filter_sbang(self):
        # Filter sbang before install so Spack's sbang hook can fix it up
        perl = join_path(self.spec['perl'].prefix.bin, 'perl')
        files = ['perl/feedGnuplot'] + glob.glob('filters/*')

        filter_file('^#!/usr/bin/perl', '#!{0}'.format(perl), *files)

    def install(self, spec, prefix):
        if self.compiler.name not in self.supported_compilers:
            raise RuntimeError('{0} is not a supported compiler \
            to compile Likwid'.format(self.compiler.name))

        filter_file('^COMPILER .*',
                    'COMPILER = ' +
                    self.supported_compilers[self.compiler.name],
                    'config.mk')
        filter_file('^PREFIX .*',
                    'PREFIX = ' +
                    prefix,
                    'config.mk')

        filter_file('^INSTALL_CHOWN.*',
                    'INSTALL_CHOWN = -o $(USER)',
                    'config.mk')

        make()
        make('install')
