import json

from apps.parabola.LogFormater import get_logger
from apps.parabola.mq_adapter.TaskAnalyzer import DeployTaskAnalyser
from apps.parabola.mq_adapter.TaskAnalyzer import CloseTaskAnalyser
from apps.parabola.mq_adapter.TaskAnalyzer import OrdinarilyAnalyser
from apps.parabola.mq_adapter.TaskAnalyzer import HeartbeatAnalyser
import apps.parabola.static as data

LOG_TASK_HANDLER = get_logger(__name__)


class TaskRouter(object):

    @staticmethod
    def deliver_task(task):
        router = {
            'DEPLOY': DeployTaskAnalyser,
            'START': OrdinarilyAnalyser,
            'PAUSE': OrdinarilyAnalyser,
            'UNPAUSE': OrdinarilyAnalyser,
            'CLOSE': CloseTaskAnalyser,
            'heartbeat': HeartbeatAnalyser
        }

        deal_msg = json.loads(task)
        worker = router.get(deal_msg[data.MSG.TASKNAME], None)
        if not worker:
            LOG_TASK_HANDLER.error('no such task~~~~!!!!!!!')
            raise NameError("%s, task type has no handler"%(deal_msg[data.MSG.TASKNAME]))

        worker(deal_msg).do_task()
