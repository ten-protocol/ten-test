import os
from pysys.constants import *
from collections import namedtuple
from ten.test.utils.properties import Properties
BuildInfo = namedtuple('BuildInfo', 'branch hash date')


class GnuplotHelper:

    @classmethod
    def graph(cls, test, command_file, *args):
        """Run gnuplot on a command input file."""
        stdout = os.path.join(test.output, os.path.basename(command_file).split('.')[0]+'.out')
        stderr = os.path.join(test.output, os.path.basename(command_file).split('.')[0]+'.err')

        arguments = ['-c', command_file]
        arguments.append('\"%s\"' % test.descriptor.title)
        arguments.append('%s' % test.descriptor.id)
        arguments.extend(args)
        test.startProcess(command=Properties().gnuplot_binary(), displayName='gnuplot', workingDir=test.output,
                          arguments=arguments, stdout=stdout, stderr=stderr, state=FOREGROUND, ignoreExitStatus=True)

    @classmethod
    def buildInfo(cls):
        """Return build info from a build log if it exists."""
        ifile = os.path.join(PROJECT.root,'artifacts','build.info')
        branch, hash, date = '', '', ''
        if os.path.exists(ifile):
            with open(ifile, 'r') as fp:
                for line in fp.readlines():
                    if line.startswith('BRANCH:'): branch = line.split(':')[1].strip()
                    if line.startswith('HASH:'): hash = (line.split(':')[1].strip())[:8]
                    if line.startswith('DATE:'): date = line.replace('DATE:','').strip()
        branch = branch.replace('_', r'\_')
        return BuildInfo(branch, hash, date)