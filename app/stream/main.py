import os
import argparse
from omegaconf import OmegaConf
#
from streamers_manager import StreamersManager

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--conf', help='YAML config file')

    args = parser.parse_args()
    conf = OmegaConf.load(args.conf)

    try:
        manager = StreamersManager.from_conf(
            conf_streamers=conf.streamers,
            conf_logs=conf.logs,
            conf_cache=conf.redis,
            conf_broker=conf.kafka
        )

        manager.start_all()
    except KeyboardInterrupt:
        manager.interrupt_all()
