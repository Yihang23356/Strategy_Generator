import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Optional


DEFAULT_FORMAT = (
    "%(asctime)s | %(levelname)s | %(name)s | "
    "%(filename)s:%(lineno)d | %(message)s"
)
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logger(
    name: str = "strategy_planner",
    level: int = logging.INFO,
    log_dir: Optional[str] = None,
    log_file: Optional[str] = None,
    to_console: bool = True,
    to_file: bool = True,
) -> logging.Logger:
    """创建并配置项目 logger（可重复调用，不会重复挂载 handler）。"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    if logger.handlers:
        return logger

    formatter = logging.Formatter(DEFAULT_FORMAT, datefmt=DEFAULT_DATE_FORMAT)

    if to_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if to_file:
        root_dir = Path(__file__).resolve().parent.parent
        target_dir = Path(log_dir) if log_dir else (root_dir / "log")
        target_dir.mkdir(parents=True, exist_ok=True)

        file_name = log_file if log_file else f"{name}.log"
        file_path = target_dir / file_name
        file_handler = TimedRotatingFileHandler(
            filename=str(file_path),
            when="midnight",
            interval=1,
            backupCount=14,
            encoding="utf-8",
        )
        file_handler.suffix = "%Y-%m-%d"
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "strategy_planner") -> logging.Logger:
    """获取 logger；首次调用时自动按默认配置初始化。"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name=name)
    return logger
