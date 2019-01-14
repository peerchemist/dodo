from appdirs import user_config_dir
import logging
import configparser
import os
from dodo.default_conf import default_conf

conf_dir = user_config_dir("dodo")
conf_file = os.path.join(conf_dir, "dodo.conf")
logfile = os.path.join(conf_dir, "dodo.log")


def write_default_config(conf_file=None):
    print("writing default config")
    config = configparser.ConfigParser()
    config["settings"] = default_conf
    config["alias"] = {}
    if not conf_file:
        config.write()
    else:
        with open(conf_file, 'w') as configfile:
            config.write(configfile)


optional = {
    "proxy": "",
    "timeout": ""
    }


def read_conf(conf_file):
    """read the configuration file"""

    config = configparser.ConfigParser()
    config.read(conf_file)
    try:
        settings = dict(config["settings"])
        for k, v in optional.items():
            settings[k] = settings.get(k, v)

        alias = dict(config["alias"])

    except KeyError:
        print("config is outdated, saving current default config to", conf_file + ".sample")
        write_default_config(conf_file + ".sample")
        raise

    return settings, alias


def init_config():
    '''if first run, setup local configuration directory.'''

    if not os.path.exists(conf_dir):
        os.mkdir(conf_dir)
    if not os.path.exists(conf_file):
        write_default_config(conf_file)


def load_conf():
    '''load user configuration'''

    init_config()

    class Settings:
        pass

    settings = read_conf(conf_file)[0]

    for key in settings:
        setattr(Settings, key, settings[key])

    setattr(Settings, "alias", read_conf(conf_file)[1])

    logging.basicConfig(filename=logfile, level=logging.getLevelName(Settings.loglevel))
    logging.basicConfig(level=logging.getLevelName(Settings.loglevel),
                        format="%(asctime)s %(levelname)s %(message)s")

    logging.debug("logging initialized")

    return Settings


Settings = load_conf()
