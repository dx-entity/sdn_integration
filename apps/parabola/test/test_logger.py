from oslo_log import log as logging


def gen_log(msg):
    logging.set_defaults(logging_context_format_string="[%(asctime)s] %(name)s {%(filename)s:line %(lineno)d} %(levelname)s: %(message)s",
                         default_log_levels=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info(msg)
    return


gen_log('kkkk')