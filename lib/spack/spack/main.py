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
"""This is the implementation of the Spack command line executable.

In a normal Spack installation, this is invoked from the bin/spack script
after the system path is set up.
"""
from __future__ import print_function

import sys
import os
import inspect
import pstats
import argparse
from six import StringIO

import llnl.util.tty as tty
from llnl.util.tty.log import log_output

import spack
from spack.error import SpackError


# names of profile statistics
stat_names = pstats.Stats.sort_arg_dict_default

# help levels in order of detail (i.e., number of commands shown)
levels = ['short', 'long']

# intro text for help at different levels
intro_by_level = {
    'short': 'These are common spack commands:',
    'long':  'Complete list of spack commands:',
}

# control top-level spack options shown in basic vs. advanced help
options_by_level = {
    'short': ['h', 'k', 'V', 'color'],
    'long': 'all'
}

# Longer text for each section, to show in help
section_descriptions = {
    'admin':       'administration',
    'basic':       'query packages',
    'build':       'build packages',
    'config':      'configuration',
    'developer':   'developer',
    'environment': 'environment',
    'extensions':  'extensions',
    'help':        'more help',
    'packaging':   'create packages',
    'system':      'system',
}

# preferential command order for some sections (e.g., build pipeline is
# in execution order, not alphabetical)
section_order = {
    'basic': ['list', 'info', 'find'],
    'build': ['fetch', 'stage', 'patch', 'configure', 'build', 'restage',
              'install', 'uninstall', 'clean']
}

# Properties that commands are required to set.
required_command_properties = ['level', 'section', 'description']


def set_working_dir():
    """Change the working directory to getcwd, or spack prefix if no cwd."""
    try:
        spack.spack_working_dir = os.getcwd()
    except OSError:
        os.chdir(spack.spack_prefix)
        spack.spack_working_dir = spack.spack_prefix


def add_all_commands(parser):
    """Add all spack subcommands to the parser."""
    for cmd in spack.cmd.commands:
        parser.add_command(cmd)


def index_commands():
    """create an index of commands by section for this help level"""
    index = {}
    for command in spack.cmd.commands:
        cmd_module = spack.cmd.get_module(command)

        # make sure command modules have required properties
        for p in required_command_properties:
            prop = getattr(cmd_module, p, None)
            if not prop:
                tty.die("Command doesn't define a property '%s': %s"
                        % (p, command))

        # add commands to lists for their level and higher levels
        for level in reversed(levels):
            level_sections = index.setdefault(level, {})
            commands = level_sections.setdefault(cmd_module.section, [])
            commands.append(command)
            if level == cmd_module.level:
                break

    return index


class SpackArgumentParser(argparse.ArgumentParser):
    def format_help_sections(self, level):
        """Format help on sections for a particular verbosity level.

        Args:
            level (str): 'short' or 'long' (more commands shown for long)
        """
        if level not in levels:
            raise ValueError("level must be one of: %s" % levels)

        # lazily add all commands to the parser when needed.
        add_all_commands(self)

        """Print help on subcommands in neatly formatted sections."""
        formatter = self._get_formatter()

        # Create a list of subcommand actions. Argparse internals are nasty!
        # Note: you can only call _get_subactions() once.  Even nastier!
        if not hasattr(self, 'actions'):
            self.actions = self._subparsers._actions[-1]._get_subactions()

        # make a set of commands not yet added.
        remaining = set(spack.cmd.commands)

        def add_group(group):
            formatter.start_section(group.title)
            formatter.add_text(group.description)
            formatter.add_arguments(group._group_actions)
            formatter.end_section()

        def add_subcommand_group(title, commands):
            """Add informational help group for a specific subcommand set."""
            cmd_set = set(c for c in commands)

            # make a dict of commands of interest
            cmds = dict((a.metavar, a) for a in self.actions
                        if a.metavar in cmd_set)

            # add commands to a group in order, and add the group
            group = argparse._ArgumentGroup(self, title=title)
            for name in commands:
                group._add_action(cmds[name])
                if name in remaining:
                    remaining.remove(name)
            add_group(group)

        # select only the options for the particular level we're showing.
        show_options = options_by_level[level]
        if show_options != 'all':
            opts = dict((opt.option_strings[0].strip('-'), opt)
                        for opt in self._optionals._group_actions)

            new_actions = [opts[letter] for letter in show_options]
            self._optionals._group_actions = new_actions

        options = ''.join(opt.option_strings[0].strip('-')
                          for opt in self._optionals._group_actions)

        index = index_commands()

        # usage
        formatter.add_text(
            "usage: %s [-%s] <command> [...]" % (self.prog, options))

        # description
        formatter.add_text(self.description)

        # start subcommands
        formatter.add_text(intro_by_level[level])

        # add argument groups based on metadata in commands
        sections = index[level]
        for section in sorted(sections):
            if section == 'help':
                continue   # Cover help in the epilog.

            group_description = section_descriptions.get(section, section)

            to_display = sections[section]
            commands = []

            # add commands whose order we care about first.
            if section in section_order:
                commands.extend(cmd for cmd in section_order[section]
                                if cmd in to_display)

            # add rest in alphabetical order.
            commands.extend(cmd for cmd in sorted(sections[section])
                            if cmd not in commands)

            # add the group to the parser
            add_subcommand_group(group_description, commands)

        # optionals
        add_group(self._optionals)

        # epilog
        formatter.add_text("""\
{help}:
  spack help --all       list all available commands
  spack help <command>   help on a specific command
  spack help --spec      help on the spec syntax
  spack docs             open http://spack.rtfd.io/ in a browser"""
.format(help=section_descriptions['help']))

        # determine help from format above
        return formatter.format_help()

    def add_command(self, cmd_name):
        """Add one subcommand to this parser."""
        # lazily initialize any subparsers
        if not hasattr(self, 'subparsers'):
            # remove the dummy "command" argument.
            if self._actions[-1].dest == 'command':
                self._remove_action(self._actions[-1])
            self.subparsers = self.add_subparsers(metavar='COMMAND',
                                                  dest="command")

        # each command module implements a parser() function, to which we
        # pass its subparser for setup.
        module = spack.cmd.get_module(cmd_name)
        subparser = self.subparsers.add_parser(
            cmd_name, help=module.description, description=module.description)
        module.setup_parser(subparser)
        return module

    def format_help(self, level='short'):
        if self.prog == 'spack':
            # use format_help_sections for the main spack parser, but not
            # for subparsers
            return self.format_help_sections(level)
        else:
            # in subparsers, self.prog is, e.g., 'spack install'
            return super(SpackArgumentParser, self).format_help()


def make_argument_parser():
    """Create an basic argument parser without any subcommands added."""
    parser = SpackArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter, add_help=False,
        description=(
            "A flexible package manager that supports multiple versions,\n"
            "configurations, platforms, and compilers."))

    # stat names in groups of 7, for nice wrapping.
    stat_lines = list(zip(*(iter(stat_names),) * 7))

    parser.add_argument('-h', '--help', action='store_true',
                        help="show this help message and exit")
    parser.add_argument('--color', action='store', default='auto',
                        choices=('always', 'never', 'auto'),
                        help="when to colorize output; default is auto")
    parser.add_argument('-d', '--debug', action='store_true',
                        help="write out debug logs during compile")
    parser.add_argument('-D', '--pdb', action='store_true',
                        help="run spack under the pdb debugger")
    parser.add_argument('-k', '--insecure', action='store_true',
                        help="do not check ssl certificates when downloading")
    parser.add_argument('-m', '--mock', action='store_true',
                        help="use mock packages instead of real ones")
    parser.add_argument('-p', '--profile', action='store_true',
                        dest='spack_profile',
                        help="profile execution using cProfile")
    parser.add_argument('-P', '--sorted-profile', default=None, metavar="STAT",
                        help="profile and sort by one or more of:\n[%s]" %
                        ',\n '.join([', '.join(line) for line in stat_lines]))
    parser.add_argument('--lines', default=20, action='store',
                        help="lines of profile output; default 20; or 'all'")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="print additional output during builds")
    parser.add_argument('-s', '--stacktrace', action='store_true',
                        help="add stacktraces to all printed statements")
    parser.add_argument('-V', '--version', action='store_true',
                        help='show version number and exit')
    return parser


def setup_main_options(args):
    """Configure spack globals based on the basic options."""
    # Set up environment based on args.
    tty.set_verbose(args.verbose)
    tty.set_debug(args.debug)
    tty.set_stacktrace(args.stacktrace)
    spack.debug = args.debug

    if spack.debug:
        import spack.util.debug as debug
        debug.register_interrupt_handler()

    if args.mock:
        from spack.repository import RepoPath
        spack.repo.swap(RepoPath(spack.mock_packages_path))

    # If the user asked for it, don't check ssl certs.
    if args.insecure:
        tty.warn("You asked for --insecure. Will NOT check SSL certificates.")
        spack.insecure = True

    # when to use color (takes always, auto, or never)
    tty.color.set_color_when(args.color)


def allows_unknown_args(command):
    """Implements really simple argument injection for unknown arguments.

    Commands may add an optional argument called "unknown args" to
    indicate they can handle unknonwn args, and we'll pass the unknown
    args in.
    """
    info = dict(inspect.getmembers(command))
    varnames = info['__code__'].co_varnames
    argcount = info['__code__'].co_argcount
    return (argcount == 3 and varnames[2] == 'unknown_args')


def _invoke_spack_command(command, parser, args, unknown_args):
    """Run a spack command *without* setting spack global options."""
    if allows_unknown_args(command):
        return_val = command(parser, args, unknown_args)
    else:
        if unknown_args:
            tty.die('unrecognized arguments: %s' % ' '.join(unknown_args))
        return_val = command(parser, args)

    # Allow commands to return and error code if they want
    return 0 if return_val is None else return_val


class SpackCommand(object):
    """Callable object that invokes a spack command (for testing).

    Example usage::

        install = SpackCommand('install')
        install('-v', 'mpich')

    Use this to invoke Spack commands directly from Python and check
    their output.
    """
    def __init__(self, command):
        """Create a new SpackCommand that invokes ``command`` when called.

        Args:
            command (str): name of the command to invoke
        """
        self.parser = make_argument_parser()
        self.parser.add_command(command)
        self.command_name = command
        self.command = spack.cmd.get_command(command)

    def __call__(self, *argv, **kwargs):
        """Invoke this SpackCommand.

        Args:
            argv (list of str): command line arguments.

        Keyword Args:
            fail_on_error (optional bool): Don't raise an exception on error

        Returns:
            (str): combined output and error as a string

        On return, if ``fail_on_error`` is False, return value of command
        is set in ``returncode`` property, and the error is set in the
        ``error`` property.  Otherwise, raise an error.
        """
        # set these before every call to clear them out
        self.returncode = None
        self.error = None

        args, unknown = self.parser.parse_known_args(
            [self.command_name] + list(argv))

        fail_on_error = kwargs.get('fail_on_error', True)

        out = StringIO()
        try:
            with log_output(out):
                self.returncode = _invoke_spack_command(
                    self.command, self.parser, args, unknown)

        except SystemExit as e:
            self.returncode = e.code

        except BaseException as e:
            self.error = e
            if fail_on_error:
                raise

        if fail_on_error and self.returncode not in (None, 0):
            raise SpackCommandError(
                "Command exited with code %d: %s(%s)" % (
                    self.returncode, self.command_name,
                    ', '.join("'%s'" % a for a in argv)))

        return out.getvalue()


def _main(command, parser, args, unknown_args):
    """Run a spack command *and* set spack globaloptions."""
    # many operations will fail without a working directory.
    set_working_dir()

    # only setup main options in here, after the real parse (we'll get it
    # wrong if we do it after the initial, partial parse)
    setup_main_options(args)
    spack.hooks.pre_run()

    # Now actually execute the command
    try:
        return _invoke_spack_command(command, parser, args, unknown_args)
    except SpackError as e:
        e.die()  # gracefully die on any SpackErrors
    except Exception as e:
        if spack.debug:
            raise
        tty.die(str(e))
    except KeyboardInterrupt:
        sys.stderr.write('\n')
        tty.die("Keyboard interrupt.")


def _profile_wrapper(command, parser, args, unknown_args):
    import cProfile

    try:
        nlines = int(args.lines)
    except ValueError:
        if args.lines != 'all':
            tty.die('Invalid number for --lines: %s' % args.lines)
        nlines = -1

    # allow comma-separated list of fields
    sortby = ['time']
    if args.sorted_profile:
        sortby = args.sorted_profile.split(',')
        for stat in sortby:
            if stat not in stat_names:
                tty.die("Invalid sort field: %s" % stat)

    try:
        # make a profiler and run the code.
        pr = cProfile.Profile()
        pr.enable()
        return _main(command, parser, args, unknown_args)

    finally:
        pr.disable()

        # print out profile stats.
        stats = pstats.Stats(pr)
        stats.sort_stats(*sortby)
        stats.print_stats(nlines)


def main(argv=None):
    """This is the entry point for the Spack command.

    Args:
        argv (list of str or None): command line arguments, NOT including
            the executable name. If None, parses from sys.argv.
    """
    # Create a parser with a simple positional argument first.  We'll
    # lazily load the subcommand(s) we need later. This allows us to
    # avoid loading all the modules from spack.cmd when we don't need
    # them, which reduces startup latency.
    parser = make_argument_parser()
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args, unknown = parser.parse_known_args(argv)

    # Just print help and exit if run with no arguments at all
    no_args = (len(sys.argv) == 1) if argv is None else (len(argv) == 0)
    if no_args:
        parser.print_help()
        return 1

    # -h and -V are special as they do not require a command, but all the
    # other options do nothing without a command.
    if not args.command:
        if args.version:
            print(spack.spack_version)
            return 0
        else:
            parser.print_help()
            return 0 if args.help else 1

    # Try to load the particular command the caller asked for.  If there
    # is no module for it, just die.
    cmd_name = args.command[0]
    try:
        parser.add_command(cmd_name)
    except ImportError:
        if spack.debug:
            raise
        tty.die("Unknown command: %s" % args.command[0])

    # Re-parse with the proper sub-parser added.
    args, unknown = parser.parse_known_args()

    # we now know whether options go with spack or the command
    if args.version:
        print(spack.spack_version)
        return 0
    elif args.help:
        parser.print_help()
        return 0

    # now we can actually execute the command.
    command = spack.cmd.get_command(cmd_name)
    try:
        if args.spack_profile or args.sorted_profile:
            _profile_wrapper(command, parser, args, unknown)
        elif args.pdb:
            import pdb
            pdb.runctx('_main(command, parser, args, unknown)',
                       globals(), locals())
            return 0
        else:
            return _main(command, parser, args, unknown)

    except SystemExit as e:
        return e.code


class SpackCommandError(Exception):
    """Raised when SpackCommand execution fails."""
