import uuid
from pysys.writer import BaseResultsWriter
from ten.test.persistence.results import OutomeResultsPersistence

class PersistenceTestsWriter(BaseResultsWriter):

    def __init__(self, logfile=None, **kwargs):
        super().__init__(logfile, **kwargs)
        self.user_dir = None
        self.machine_name = None
        self.is_cloud_vm = None
        self.outcomes_db = None

    def setup(self, numTests=0, cycles=1, xargs=None, threads=0, testoutdir=u'', runner=None, **kwargs):
        self.uuid = uuid.uuid4().hex
        self.env = runner.ten_runner.env
        self.user_dir = runner.ten_runner.user_dir
        self.machine_name = runner.ten_runner.machine_name
        self.is_cloud_vm = runner.ten_runner.is_cloud_vm
        runner.log.info('Run uuid is %s' % self.uuid)

        # use remote persistence if we are running in azure
        self.outcomes_db = OutomeResultsPersistence.init(self.is_cloud_vm, self.user_dir, self.machine_name)

    def cleanup(self, **kwargs):
        self.outcomes_db.close()

    def processResult(self, testObj, **kwargs):
        self.outcomes_db.insert(self.uuid,
                                testObj.descriptor.id,
                                self.env,
                                int(kwargs['testStart']),
                                kwargs['testTime'],
                                str(testObj.getOutcome()))
