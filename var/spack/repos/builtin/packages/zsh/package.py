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


class Zsh(AutotoolsPackage):
    """Zsh is a shell designed for interactive use, although it is also a
    powerful scripting language. Many of the useful features of bash, ksh, and
    tcsh were incorporated into zsh; many original features were added.
    """

    homepage = "http://www.zsh.org"
    url = "http://downloads.sourceforge.net/project/zsh/zsh/5.4.2/zsh-5.4.2.tar.gz"

    version('5.4.2', checksum='dfe156fd69b0d8d1745ecf6d6e02e047')
    version('5.3.1', checksum='d583fbca0c2410bf9542ce8a651c26ca')
    version('5.1.1', checksum='8ba28a9ef82e40c3a271602f18343b2f')

    # Testing for terminal related things causes failures in e.g. Jenkins.
    # See e.g. https://www.zsh.org/mla/users/2003/msg00845.html,
    # although the name of the option has evolved since then.
    variant('skip-tcsetpgrp-test', default=True,
            description="Skip configure's tcsetpgrp test")

    depends_on("pcre")
    depends_on("ncurses")

    def configure_args(self):
        if '+skip-tcsetpgrp-test' in self.spec:
            # assert that we have a functional tcsetpgrp
            args = ['--with-tcsetpgrp']
        else:
            # let configure run it's test and see what's what
            args = []

        return args
