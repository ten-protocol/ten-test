import os
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
    def container_id(cls, test, name, *args):
        stdout = os.path.join(test.output, 'docker_cntid_%s'%name+'.out')
        stderr = os.path.join(test.output, 'docker_cntid_%s'%name+'.err')

        arguments = ['ps', '-aqf', 'name=%s'%name]
        test.startProcess(command=Properties().docker_binary(), displayName='docker-ps', workingDir=test.output,
                          arguments=arguments, stdout=stdout, stderr=stderr, state=FOREGROUND, ignoreExitStatus=True)

        with open(stdout, 'r') as fp: return fp.readline().strip()

    @classmethod
    def container_stop(cls, test, name, *args):
        stdout = os.path.join(test.output, 'docker_stop_%s'%name+'.out')
        stderr = os.path.join(test.output, 'docker_stop_%s'%name+'.err')
        id = cls.container_id(test, name, args)

        arguments = ['stop', id]
        test.startProcess(command=Properties().docker_binary(), displayName='docker-stop', workingDir=test.output,
                          arguments=arguments, stdout=stdout, stderr=stderr, state=FOREGROUND, ignoreExitStatus=True)

    @classmethod
    def container_start(cls, test, name, *args):
        stdout = os.path.join(test.output, 'docker_start_%s'%name+'.out')
        stderr = os.path.join(test.output, 'docker_start_%s'%name+'.err')
        id = cls.container_id(test, name, args)

        log = cls.container_logs(test, name, args)
        num_start = count_string_in_file(log, 'Server started.')
        test.log.info('Container %s has been started %d times already' % (id, num_start))
        arguments = ['start', id]
        test.startProcess(command=Properties().docker_binary(), displayName='docker-start', workingDir=test.output,
                          arguments=arguments, stdout=stdout, stderr=stderr, state=FOREGROUND, ignoreExitStatus=True)

        count = 0
        while (count < 20):
            log = cls.container_logs(test, name, args)
            starts = count_string_in_file(log, 'Server started.')
            if (starts == num_start+1): break
            test.log.info('Waiting for the container to be restarted')
            test.wait(2.0)
            count = count + 1

    @classmethod
    def container_logs(cls, test, name, *args):
        stdout = os.path.join(test.output, 'docker_logs_%s'%name+'.out')
        stderr = os.path.join(test.output, 'docker_logs_%s'%name+'.err')
        id = cls.container_id(test, name, args)

        arguments = ['logs', id]
        test.startProcess(command=Properties().docker_binary(), displayName='docker-start', workingDir=test.output,
                          arguments=arguments, stdout=stdout, stderr=stderr, state=FOREGROUND, ignoreExitStatus=True)
        return stdout