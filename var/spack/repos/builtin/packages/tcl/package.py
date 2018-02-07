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


class Tcl(AutotoolsPackage):
    """Tcl (Tool Command Language) is a very powerful but easy to
       learn dynamic programming language, suitable for a very wide
       range of uses, including web and desktop applications,
       networking, administration, testing and many more. Open source
       and business-friendly, Tcl is a mature yet evolving language
       that is truly cross platform, easily deployed and highly
       extensible."""
    homepage = "http://www.tcl.tk"
    url      = "http://prdownloads.sourceforge.net/tcl/tcl8.6.5-src.tar.gz"

    version('8.6.6', '5193aea8107839a79df8ac709552ecb7')
    version('8.6.5', '0e6426a4ca9401825fbc6ecf3d89a326')
    version('8.6.4', 'd7cbb91f1ded1919370a30edd1534304')
    version('8.6.3', 'db382feca91754b7f93da16dc4cdad1f')
    version('8.5.19', '0e6426a4ca9401825fbc6ecf3d89a326')

    depends_on('zlib')

    configure_directory = 'unix'

    def setup_environment(self, spack_env, run_env):
        # When using Tkinter from within spack provided python+tk, python
        # will not be able to find Tcl/Tk unless TCL_LIBRARY is set.
        run_env.set('TCL_LIBRARY', join_path(self.prefix.lib, 'tcl{0}'.format(
            self.spec.version.up_to(2))))

    def install(self, spec, prefix):
        with working_dir(self.build_directory):
            make('install')

            # Some applications like Expect require private Tcl headers.
            make('install-private-headers')

    @run_after('install')
    def symlink_tclsh(self):
        with working_dir(self.prefix.bin):
            symlink('tclsh{0}'.format(self.version.up_to(2)), 'tclsh')
