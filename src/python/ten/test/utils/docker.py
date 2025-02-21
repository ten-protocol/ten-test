import os, time
from pysys.constants import FOREGROUND
from ten.test.utils.properties import Properties


def count_string_in_file(filename, search_string):
    try:
        with open(filename, 'r') as file:
            content = file.read()
            count = content.count(search_string)
        return count
    except FileNotFoundError:
        return None


class DockerHelper:

    @classmethod
    def container_id(cls, test, name):
        stdout = os.path.join(test.output, 'docker_cntid_%s'%name+'.out')
        stderr = os.path.join(test.output, 'docker_cntid_%s'%name+'.err')

        arguments = ['ps', '-aqf', 'name=%s'%name]
        test.startProcess(command=Properties().docker_binary(), displayName='docker-ps', workingDir=test.output,
                          arguments=arguments, stdout=stdout, stderr=stderr, state=FOREGROUND,
                          ignoreExitStatus=True, quiet=True)

        with open(stdout, 'r') as fp: return fp.readline().strip()

    @classmethod
    def container_stop(cls, test, name):
        stdout = os.path.join(test.output, 'docker_stop_%s'%name+'.out')
        stderr = os.path.join(test.output, 'docker_stop_%s'%name+'.err')
        id = cls.container_id(test, name)
        test.log.info('Stopping container %s with id %s' % (name, id))

        arguments = ['stop', id]
        test.startProcess(command=Properties().docker_binary(), displayName='docker-stop', workingDir=test.output,
                          arguments=arguments, stdout=stdout, stderr=stderr, state=FOREGROUND,
                          ignoreExitStatus=True, quiet=True)

    @classmethod
    def container_start(cls, test, name, search_msg):
        stdout = os.path.join(test.output, 'docker_start_%s'%name+'.out')
        stderr = os.path.join(test.output, 'docker_start_%s'%name+'.err')
        id = cls.container_id(test, name)

        log = cls.container_logs(test, name)
        restarts = count_string_in_file(log, search_msg)
        test.log.info('Starting container %s with id %s (previous restarts %d)' % (name, id, restarts))

        arguments = ['start', id]
        test.startProcess(command=Properties().docker_binary(), displayName='docker-start', workingDir=test.output,
                          arguments=arguments, stdout=stdout, stderr=stderr, state=FOREGROUND,
                          ignoreExitStatus=True, quiet=True)

        start = time.time()
        while (count_string_in_file(cls.container_logs(test, name), search_msg) != restarts+1):
            if (time.time() - start) > 30:
                raise TimeoutError('Timed out waiting for the container to be restarted')
            test.log.info('Waiting for the container to be restarted')
            time.sleep(2.0)

    @classmethod
    def container_logs(cls, test, name):
        stdout = os.path.join(test.output, 'docker_logs_%s'%name+'.out')
        stderr = os.path.join(test.output, 'docker_logs_%s'%name+'.err')
        id = cls.container_id(test, name)

        arguments = ['logs', id]
        test.startProcess(command=Properties().docker_binary(), displayName='docker-start', workingDir=test.output,
                          arguments=arguments, stdout=stdout, stderr=stderr, state=FOREGROUND,
                          ignoreExitStatus=True, quiet=True)
        return stdout