import os, re
from pysys.constants import FOREGROUND
from obscuro.test.utils.properties import Properties

class Docker:
    """A wrapper over Docker. """

    @classmethod
    def get_id_from_name(cls, test, name):
        """Return the container id from the container name. """
        props = Properties()
        binary = props.docker_binary()
        stdout = os.path.join(test.output, 'docker_get_id.out')
        stderr = os.path.join(test.output, 'docker_get_id.err')

        arguments = ['ps', '-aq', '-f', 'name=%s' % name]
        test.startProcess(command=binary, displayName='docker',
                          workingDir=test.output, environs=os.environ, quiet=True,
                          arguments=arguments, stdout=stdout, stderr=stderr, state=FOREGROUND)
        with open(stdout, 'r') as fp: container_id = fp.readline().strip()
        return container_id

    @classmethod
    def get_logs(cls, test, container_id):
        """Return the container id from the container name. """
        props = Properties()
        binary = props.docker_binary()
        stdout = os.path.join(test.output, 'docker_logs_%s.out' % container_id)
        stderr = os.path.join(test.output, 'docker_logs_%s.err' % container_id)

        arguments = ['logs', container_id]
        test.startProcess(command=binary, displayName='docker',
                          workingDir=test.output, environs=os.environ, quiet=True,
                          arguments=arguments, stdout=stdout, stderr=stderr, state=FOREGROUND)
        return stdout

    @classmethod
    def get_l1_start(cls, filename):
        p = re.compile('L1Start=(.*)$')
        with open(filename, mode="rt") as fp:
            lines = fp.read()
            images = re.findall(p, lines)
        return images
