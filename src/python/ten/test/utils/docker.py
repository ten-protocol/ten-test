import os
from pysys.constants import FOREGROUND, BACKGROUND
from ten.test.utils.properties import Properties


class DockerHelper:

    @classmethod
    def container_id(cls, test, container, name=None):
        """Get a docker container id by name. """
        basename = 'docker_id_%s' % container if name is None else 'docker_id_%s_%s' % (container, name)
        stdout = os.path.join(test.output, '%s.out' % basename)
        stderr = os.path.join(test.output, '%s.err' % basename)

        arguments = ['ps', '-aqf', 'name=%s' % container]
        test.startProcess(command=Properties().docker_binary(), displayName='docker-ps', workingDir=test.output,
                          arguments=arguments, stdout=stdout, stderr=stderr, state=FOREGROUND,
                          ignoreExitStatus=True, quiet=True)

        with open(stdout, 'r') as fp: return fp.readline().strip()

    @classmethod
    def container_stop(cls, test, container, time=10, name=None):
        """Stop a docker container by name.

        Sends a SIGTERM to gracefully stop the container. If the container does not stop within the time period
        supplied, a SIGKILL is then sent. To immediately send a SIGKILL, set time to zero.
        """
        basename = 'docker_stop_%s' % container if name is None else 'docker_stop_%s_%s' % (container, name)
        stdout = os.path.join(test.output, '%s.out' % basename)
        stderr = os.path.join(test.output, '%s.err' % basename)

        id = cls.container_id(test, container)
        test.log.info('Stopping container %s with id %s, time %d' % (container, id, time))

        arguments = ['stop', '-t=%d' % time, id]
        test.startProcess(command=Properties().docker_binary(), displayName='docker-stop', workingDir=test.output,
                          arguments=arguments, stdout=stdout, stderr=stderr, state=FOREGROUND,
                          ignoreExitStatus=True, quiet=True)

    @classmethod
    def container_start(cls, test, container, name=None):
        """Start a docker container by name. """
        basename = 'docker_start_%s' % container if name is None else 'docker_start_%s_%s' % (container, name)
        stdout = os.path.join(test.output, '%s.out' % basename)
        stderr = os.path.join(test.output, '%s.err' % basename)

        id = cls.container_id(test, container)
        test.log.info('Starting container %s with id %s' % (container, id))

        arguments = ['start', id]
        test.startProcess(command=Properties().docker_binary(), displayName='docker-start', workingDir=test.output,
                          arguments=arguments, stdout=stdout, stderr=stderr, state=FOREGROUND,
                          ignoreExitStatus=True, quiet=True)

    @classmethod
    def container_rm(cls, test, container, name=None):
        """Remove a docker container by name. """
        basename = 'docker_rm_%s' % container if name is None else 'docker_rm_%s_%s' % (container, name)
        stdout = os.path.join(test.output, '%s.out' % basename)
        stderr = os.path.join(test.output, '%s.err' % basename)

        id = cls.container_id(test, container)
        if id == '':
            test.log.info('No container exists')
            return
        test.log.info('Removing container %s with id %s' % (container, id))

        arguments = ['container', 'rm', id]
        test.startProcess(command=Properties().docker_binary(), displayName='docker-rm', workingDir=test.output,
                          arguments=arguments, stdout=stdout, stderr=stderr, state=FOREGROUND,
                          ignoreExitStatus=True, quiet=True)

    @classmethod
    def container_logs(cls, test, container, state=FOREGROUND, name=None, since=None):
        """Get the docker logs to stdout and stderr by name. """
        basename = 'docker_logs_%s' % container if name is None else '%s_%s' % (container, name)
        stdout = os.path.join(test.output, '%s.out' % basename)
        stderr = os.path.join(test.output, '%s.err' % basename)

        id = cls.container_id(test, container)

        arguments = ['logs', id]
        if since is not None: arguments.extend(['--since', '%s' % since])
        test.startProcess(command=Properties().docker_binary(), displayName='docker-logs', workingDir=test.output,
                          arguments=arguments, stdout=stdout, stderr=stderr, state=state,
                          ignoreExitStatus=True, quiet=True)
        return stdout, stderr

    @classmethod
    def container_running(cls, test, container, name=None):
        basename = 'docker_inspect_%s' % container if name is None else 'docker_inspect_%s_%s' % (container, name)
        stdout = os.path.join(test.output, '%s.out' % basename)
        stderr = os.path.join(test.output, '%s.err' % basename)

        arguments = ['inspect', '-f', '\'{{.State.Running}}\'', container]
        test.startProcess(command=Properties().docker_binary(), displayName='docker-inspect', workingDir=test.output,
                          arguments=arguments, stdout=stdout, stderr=stderr, state=FOREGROUND,
                          ignoreExitStatus=True, quiet=True)
        with open(stdout, 'r') as file: running = file.readline()
        return ('true' in running)