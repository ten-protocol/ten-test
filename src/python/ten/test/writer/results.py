import uuid, time
from pysys.writer import BaseResultsWriter
from ten.test.persistence.results import OutcomeResultsPersistence, RunTypePersistence


class PersistenceTestsWriter(BaseResultsWriter):

    def __init__(self, logfile=None, **kwargs):
        super().__init__(logfile, **kwargs)
        self.user_dir = None
        self.machine_name = None
        self.is_cloud_vm = None
        self.outcomes = []
        self.outcomes_db = None

    def setup(self, numTests=0, cycles=1, xargs=None, threads=0, testoutdir=u'', runner=None, **kwargs):
        self.runner = runner
        self.uuid = uuid.uuid4().hex
        self.start_time = int(time.time())
        self.env = runner.ten_runner.env
        self.user_dir = runner.ten_runner.user_dir
        self.run_type = runner.xargs.get('RUN_TYPE', None)
        self.machine_name = runner.ten_runner.machine_name
        self.is_cloud_vm = runner.ten_runner.is_cloud_vm

        runner.log.info('Run uuid is %s' % self.uuid)
        if self.run_type is not None: runner.log.info('Run type is %s' % self.run_type)
        runner.uuid = self.uuid

        # use remote persistence if we are running in azure
        self.outcomes_db = OutcomeResultsPersistence.init(self.is_cloud_vm, self.user_dir, self.machine_name)

    def cleanup(self, **kwargs):
        if self.run_type is not None:
            runtype_db = RunTypePersistence.init(self.is_cloud_vm, self.user_dir, self.machine_name)
            runtype_db.insert(self.uuid, self.env, self.run_type, self.start_time, all(self.outcomes))
            runtype_db.close()
        self.outcomes_db.close()

    def processResult(self, testObj, **kwargs):
        outcome = testObj.getOutcome()
        self.outcomes.append(not outcome.isFailure())
        self.outcomes_db.insert(self.uuid,
                                testObj.descriptor.id,
                                self.env,
                                int(kwargs['testStart']),
                                kwargs['testTime'],
                                testObj.cost if hasattr(testObj, 'cost') else 0,
                                str(outcome))
