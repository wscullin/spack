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
import glob


class IntelTbb(Package):
    """Widely used C++ template library for task parallelism.
    Intel Threading Building Blocks (Intel TBB) lets you easily write parallel
    C++ programs that take full advantage of multicore performance, that are
    portable and composable, and that have future-proof scalability.
    """
    homepage = "http://www.threadingbuildingblocks.org/"

    # Only version-specific URL's work for TBB
    version('2018.2', '0b8dfe30917a54e40828eeb0ed7562ae',
            url='https://github.com/01org/tbb/archive/2018_U2.tar.gz')
    version('2018.1', 'b2f2fa09adf44a22f4024049907f774b',
            url='https://github.com/01org/tbb/archive/2018_U1.tar.gz')
    version('2018.0', 'e54de69981905ad69eb9cf0226b9bf5f9a4ba065',
            url='https://github.com/01org/tbb/archive/2018.tar.gz')
    version('2017.8', '488f049fd107d8b1f6ba59cf4aad881172525106',
            url='https://github.com/01org/tbb/archive/2017_U8.tar.gz')
    version('2017.6', 'c0a722fd1ae66b40aeab25da6049086ef5f02f17',
            url='https://github.com/01org/tbb/archive/2017_U6.tar.gz')
    version('2017.5', '26f720729d322913912e99d1e4a36bd10625d3ca',
            url='https://github.com/01org/tbb/archive/2017_U5.tar.gz')
    version('2017.3', '2c451a5bcf6fc31487b98b4b29651c369874277c',
            url='https://www.threadingbuildingblocks.org/sites/default/files/software_releases/source/tbb2017_20161128oss_src.tgz')
    version('4.4.4', 'd4cee5e4ca75cab5181834877738619c56afeb71',
            url='https://www.threadingbuildingblocks.org/sites/default/files/software_releases/source/tbb44_20160413oss_src.tgz')
    version('4.4.3', '80707e277f69d9b20eeebdd7a5f5331137868ce1',
            url='https://www.threadingbuildingblocks.org/sites/default/files/software_releases/source/tbb44_20160128oss_src_0.tgz')

    provides('tbb')

    variant('shared', default=True,
            description='Builds a shared version of TBB libraries')

    # include patch for gcc rtm options
    patch("tbb_gcc_rtm_key.patch", level=0)

    def coerce_to_spack(self, tbb_build_subdir):
        for compiler in ["icc", "gcc", "clang"]:
            fs = glob.glob(join_path(tbb_build_subdir,
                                     "*.%s.inc" % compiler))
            for f in fs:
                lines = open(f).readlines()
                of = open(f, "w")
                for l in lines:
                    if l.strip().startswith("CPLUS ="):
                        of.write("# coerced to spack\n")
                        of.write("CPLUS = $(CXX)\n")
                    elif l.strip().startswith("CPLUS ="):
                        of.write("# coerced to spack\n")
                        of.write("CONLY = $(CC)\n")
                    else:
                        of.write(l)

    def install(self, spec, prefix):
        if spec.satisfies('%gcc@6.1:') and spec.satisfies('@:4.4.3'):
            raise InstallError('Only TBB 4.4.4 and above build with GCC 6.1!')

        # We need to follow TBB's compiler selection logic to get the proper
        # build + link flags but we still need to use spack's compiler wrappers
        # to accomplish this, we do two things:
        #
        # * Look at the spack spec to determine which compiler we should pass
        #   to tbb's Makefile;
        #
        # * patch tbb's build system to use the compiler wrappers (CC, CXX) for
        #   icc, gcc, clang (see coerce_to_spack());
        #
        self.coerce_to_spack("build")

        if spec.satisfies('%clang'):
            tbb_compiler = "clang"
        elif spec.satisfies('%intel'):
            tbb_compiler = "icc"
        else:
            tbb_compiler = "gcc"

        mkdirp(prefix)
        mkdirp(prefix.lib)

        make_opts = []

        # Static builds of TBB are enabled by including 'big_iron.inc' file
        # See caveats in 'big_iron.inc' for limits on using TBB statically
        # Lore states this file must be handed to make before other options
        if '+shared' not in self.spec:
            make_opts.append("extra_inc=big_iron.inc")

        #
        # tbb does not have a configure script or make install target
        # we simply call make, and try to put the pieces together
        #
        make_opts.append("compiler={0}".format(tbb_compiler))
        make(*make_opts)

        # install headers to {prefix}/include
        install_tree('include', prefix.include)

        # install libs to {prefix}/lib
        tbb_lib_names = ["libtbb",
                         "libtbbmalloc",
                         "libtbbmalloc_proxy"]

        for lib_name in tbb_lib_names:
            # install release libs
            fs = glob.glob(join_path("build", "*release", lib_name + ".*"))
            for f in fs:
                install(f, prefix.lib)
            # install debug libs if they exist
            fs = glob.glob(join_path("build", "*debug", lib_name + "_debug.*"))
            for f in fs:
                install(f, prefix.lib)
