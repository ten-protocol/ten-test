import os
from pysys.constants import FOREGROUND
from ten.test.utils.properties import Properties


class DockerHelper:

    @classmethod
    def container_id(cls, test, name, *args):
        stdout = os.path.join(test.output, 'docker_cntid_%s'%name+'.out')
        stderr = os.path.join(test.output, 'docker_cntid_%s'%name+'.err')

        arguments = ['-ps', '-aqf', '\"name=%s\"'%name]
        arguments.extend(args)
        test.startProcess(command=Properties().docker_binary(), displayName='docker', workingDir=test.output,
                          arguments=arguments, stdout=stdout, stderr=stderr, state=FOREGROUND, ignoreExitStatus=True)

        with open(stdout, 'r') as fp: return fp.readline()
