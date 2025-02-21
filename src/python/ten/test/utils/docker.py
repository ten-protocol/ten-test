import os, time
from pysys.constants import FOREGROUND
from ten.test.utils.properties import Properties


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
    def container_start(cls, test, name, timeout=60):
        stdout = os.path.join(test.output, 'docker_start_%s'%name+'.out')
        stderr = os.path.join(test.output, 'docker_start_%s'%name+'.err')
        id = cls.container_id(test, name)
        test.log.info('Starting container %s with id %s' % (name, id))

        arguments = ['start', id]
        test.startProcess(command=Properties().docker_binary(), displayName='docker-start', workingDir=test.output,
                          arguments=arguments, stdout=stdout, stderr=stderr, state=FOREGROUND,
                          ignoreExitStatus=True, quiet=True)

        test.log.info('Waiting for network to be healthy ...')
        start = time.time()
        while True:
            if (time.time() - start) > timeout: raise TimeoutError('Timed out waiting for the network to be healthy')
            ret = test.ten_health()
            test.log.info('Reported health status is %s' % ret['OverallHealth'])
            if ret['OverallHealth']: break
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