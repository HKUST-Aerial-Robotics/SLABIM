#!/usr/bin/env python
# coding: utf-8
# @author: Zhijian Qiao
# @email: zqiaoac@connect.ust.hk
from pathlib import Path
import yaml
from easydict import EasyDict
import os
import sys
import datetime
import argparse

cfg = EasyDict()
cfg.ROOT_DIR = str((Path(__file__).resolve().parent / "../../").resolve())
sys.path.append(cfg.ROOT_DIR)


class Logger:
    def __init__(self):
        filename = os.path.basename(sys.argv[0]).split(".")[0]
        self.log_dir = os.path.join(
            cfg.ROOT_DIR,
            "Log",
            "{}-{}".format(
                filename, datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            ),
        )
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        self.log_file = os.path.join(self.log_dir, "output.log")
        self.log_file = open(self.log_file, "w")

    def info(self, msg, verbose=True):
        if verbose:
            print(msg)
        self.log_file.write(msg + "\n")
        self.log_file.flush()

    def close(self):
        self.log_file.close()


logger = Logger()


def log_config_to_file(cfg, pre="cfg", logger=None):
    for key, val in cfg.items():
        if isinstance(cfg[key], EasyDict):
            logger.info("\n%s.%s = edict()" % (pre, key))
            log_config_to_file(cfg[key], pre=pre + "." + key, logger=logger)
            continue
        logger.info("%s.%s: %s" % (pre, key, val))


def cfg_from_list(cfg_list, config):
    """Set config keys via list (e.g., from command line)."""
    from ast import literal_eval

    assert len(cfg_list) % 2 == 0
    for k, v in zip(cfg_list[0::2], cfg_list[1::2]):
        key_list = k.split(".")
        d = config
        for subkey in key_list[:-1]:
            assert subkey in d, "NotFoundKey: %s" % subkey
            d = d[subkey]
        subkey = key_list[-1]
        assert subkey in d, "NotFoundKey: %s" % subkey
        try:
            value = literal_eval(v)
        except:
            value = v

        if type(value) != type(d[subkey]) and isinstance(d[subkey], EasyDict):
            key_val_list = value.split(",")
            for src in key_val_list:
                cur_key, cur_val = src.split(":")
                val_type = type(d[subkey][cur_key])
                cur_val = val_type(cur_val)
                d[subkey][cur_key] = cur_val
        elif type(value) != type(d[subkey]) and isinstance(d[subkey], list):
            val_list = value.split(",")
            for k, x in enumerate(val_list):
                val_list[k] = type(d[subkey][0])(x)
            d[subkey] = val_list
        else:
            assert type(value) == type(
                d[subkey]
            ), "type {} does not match original type {}".format(
                type(value), type(d[subkey])
            )
            d[subkey] = value


def merge_new_config(config, new_config):
    if "_BASE_CONFIG_" in new_config:
        with open(new_config["_BASE_CONFIG_"], "r") as f:
            try:
                yaml_config = yaml.safe_load(f, Loader=yaml.FullLoader)
            except:
                yaml_config = yaml.safe_load(f)
        config.update(EasyDict(yaml_config))

    for key, val in new_config.items():
        if not isinstance(val, dict):
            config[key] = val
            continue
        if key not in config:
            config[key] = EasyDict()
        merge_new_config(config[key], val)

    return config


def cfg_from_yaml_file(cfg_file, config):
    with open(cfg_file, "r") as f:
        try:
            new_config = yaml.safe_load(f, Loader=yaml.FullLoader)
        except:
            new_config = yaml.safe_load(f)

        merge_new_config(config=config, new_config=new_config)

    return config


def reset_cfg(cfg):
    cfg = EasyDict()
    cfg.ROOT_DIR = (Path(__file__).resolve().parent / "../").resolve()
    return cfg


def load_cfg(cfg_path):
    cfg_from_yaml_file(os.path.join(cfg.ROOT_DIR, cfg_path), cfg)
    return cfg
