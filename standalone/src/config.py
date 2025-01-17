import os
import sys
import yaml
import shutil
import logging


def get_logging_level():
    return os.getenv("LOGGING_LEVEL", "INFO")


def configure_logging():
    logging_level = get_logging_level().upper()
    numeric_level = getattr(logging, logging_level, None)

    if not isinstance(numeric_level, int):
        raise Exception(f"Invalid log level: {numeric_level}")

    logging.basicConfig(
        level=numeric_level,
        datefmt="%Y-%m-%d %H:%M",
        format="[%(asctime)s] [%(levelname)s] [%(module)s]: #%(funcName)s @%(lineno)d: %(message)s",
    )
    logging.info(f"Logging level: {logging_level}")


def save_config(config: dict):
    backup_config(config)
    try:
        path = config["application_path"]
        path = os.path.join(path, "config.yaml")
        config["path"] = path
        with open(path, "w", encoding='utf-8') as f:
            tmp = config.copy()
            if "whitelist" in tmp["listing_setting"]:
                tmp["listing_setting"].pop("whitelist")
            if "blacklist" in tmp["listing_setting"]:
                tmp["listing_setting"].pop("blacklist")
            yaml.dump(tmp, f, allow_unicode=True, default_flow_style=False)
    except Exception as e:
        logging.exception("")
        restore_config(config)
        raise e


def backup_config(config: dict):
    source = config["config_path"]
    destination = os.path.join(config["application_path"], "config_backup.yaml")
    shutil.copyfile(source, destination)


def restore_config(config: dict):
    destination = config["config_path"]
    source = os.path.join(config["application_path"], "config_backup.yaml")
    shutil.copyfile(source, destination)
    os.remove(source)


def load_config() -> dict:

    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
        print("EXE", application_path)
    elif __file__:
        application_path = os.getcwd()
        print("SCRIPT", application_path)

    if os.path.exists(os.path.join(application_path, "config.yaml")):
        path = os.path.join(application_path, "config.yaml")
    else:
        path = os.path.join(application_path, "config_template.yaml")

    with open(path, "r", encoding='utf-8') as f:
        config = yaml.safe_load(f)

    if "listing_setting" not in config:
        config["listing_setting"] = {
            "whitelist_activate": False,
            "blacklist_activate": False,
        }

    if "session" not in config["telegram_setting"]:
        config["telegram_setting"]["session"] = "anon"

    if "make_short" not in config["order_setting"]:
        config["order_setting"]["make_short"] = False

    config = type_casting(config)
    config["path"] = path
    config["config_path"] = path
    config["application_path"] = application_path
    load_lists(config)
    return config


def load_lists(config: dict):
    path = config["application_path"]
    try:
        content = open(os.path.join(path, "whitelist.txt"), "r").read()
        content = [i.strip() for i in content.split()]
        content = [i for i in content if i]
        config["listing_setting"]["whitelist"] = content
    except Exception:
        logging.error("Read whitelist failed.")
        config["listing_setting"]["whitelist"] = []

    try:
        content = open(os.path.join(path, "blacklist.txt"), "r").read()
        content = [i.strip() for i in content.split()]
        content = [i for i in content if i]
        config["listing_setting"]["blacklist"] = content
    except Exception:
        logging.error("Read blacklist failed.")
        config["listing_setting"]["blacklist"] = []


def save_lists(config: dict):
    path = config["application_path"]
    with open(os.path.join(path, "whitelist.txt"), "w") as f:
        for i in config["listing_setting"]["whitelist"]:
            print(i, file=f)
    with open(os.path.join(path, "blacklist.txt"), "w") as f:
        for i in config["listing_setting"]["blacklist"]:
            print(i, file=f)


def type_casting(config: dict):
    for key, value in config["order_setting"].items():
        if isinstance(value, str):
            try:
                value = float(value)
                config["order_setting"][key] = value
            except Exception:
                pass
    return config


configure_logging()
config = load_config()
