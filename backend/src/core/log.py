import logging
import sys

from loguru import logger


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging():
    logger.remove()
    logger.add(
        sys.stdout,
        level='INFO',
        enqueue=False,  # 开发模式下确保日志实时可见
        backtrace=True,
        diagnose=True,
    )

    # 统一 logger, 注释掉可以区分 fastapi 和业务的日志
    # 拦截所有相关 logger，包括 uvicorn 的
    # logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # # 必须显式接管这几个 uvicorn logger
    # for name in (
    #     'uvicorn',
    #     'uvicorn.error',
    #     'uvicorn.access',
    #     'fastapi',
    # ):
    #     log = logging.getLogger(name)
    #     log.handlers = [InterceptHandler()]
    #     log.propagate = False
