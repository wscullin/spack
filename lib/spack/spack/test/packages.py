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
import spack
import pytest

from llnl.util.filesystem import join_path
from spack.repository import Repo
from spack.util.naming import mod_to_class
from spack.spec import Spec


@pytest.mark.usefixtures('config', 'builtin_mock')
class TestPackage(object):
    def test_load_package(self):
        spack.repo.get('mpich')

    def test_package_name(self):
        pkg = spack.repo.get('mpich')
        assert pkg.name == 'mpich'

    def test_package_filename(self):
        repo = Repo(spack.mock_packages_path)
        filename = repo.filename_for_package_name('mpich')
        assert filename == join_path(
            spack.mock_packages_path,
            'packages',
            'mpich',
            'package.py'
        )

    def test_nonexisting_package_filename(self):
        repo = Repo(spack.mock_packages_path)
        filename = repo.filename_for_package_name('some-nonexisting-package')
        assert filename == join_path(
            spack.mock_packages_path,
            'packages',
            'some-nonexisting-package',
            'package.py'
        )

    def test_package_class_names(self):
        assert 'Mpich' == mod_to_class('mpich')
        assert 'PmgrCollective' == mod_to_class('pmgr_collective')
        assert 'PmgrCollective' == mod_to_class('pmgr-collective')
        assert 'Pmgrcollective' == mod_to_class('PmgrCollective')
        assert '_3db' == mod_to_class('3db')

    # Below tests target direct imports of spack packages from the
    # spack.pkg namespace
    def test_import_package(self):
        import spack.pkg.builtin.mock.mpich             # noqa

    def test_import_package_as(self):
        import spack.pkg.builtin.mock.mpich as mp       # noqa

        import spack.pkg.builtin.mock                   # noqa
        import spack.pkg.builtin.mock as m              # noqa
        from spack.pkg.builtin import mock              # noqa

    def test_inheritance_of_diretives(self):
        p = spack.repo.get('simple-inheritance')

        # Check dictionaries that should have been filled by directives
        assert len(p.dependencies) == 3
        assert 'cmake' in p.dependencies
        assert 'openblas' in p.dependencies
        assert 'mpi' in p.dependencies
        assert len(p.provided) == 2

        # Check that Spec instantiation behaves as we expect
        s = Spec('simple-inheritance')
        s.concretize()
        assert '^cmake' in s
        assert '^openblas' in s
        assert '+openblas' in s
        assert 'mpi' in s

        s = Spec('simple-inheritance~openblas')
        s.concretize()
        assert '^cmake' in s
        assert '^openblas' not in s
        assert '~openblas' in s
        assert 'mpi' in s

    def test_dependency_extensions(self):
        s = Spec('extension2')
        s.concretize()
        deps = set(x.name for x in s.package.dependency_activations())
        assert deps == set(['extension1'])

    def test_import_class_from_package(self):
        from spack.pkg.builtin.mock.mpich import Mpich  # noqa

    def test_import_module_from_package(self):
        from spack.pkg.builtin.mock import mpich        # noqa

    def test_import_namespace_container_modules(self):
        import spack.pkg                                # noqa
        import spack.pkg as p                           # noqa
        from spack import pkg                           # noqa

        import spack.pkg.builtin                        # noqa
        import spack.pkg.builtin as b                   # noqa
        from spack.pkg import builtin                   # noqa

        import spack.pkg.builtin.mock                   # noqa
        import spack.pkg.builtin.mock as m              # noqa
        from spack.pkg.builtin import mock              # noqa
