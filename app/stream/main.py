import os
import argparse
from omegaconf import OmegaConf
#
from streamers_manager import StreamersManager

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-s', '--start', help='Start streaming', action='store_true')
    group.add_argument('-e', '--enable', help='Enable streaming', action='store_true')
    group.add_argument('-d', '--disable', help='Disable streaming', action='store_true')
    group.add_argument('-i', '--interrupt', help='Interrupt streaming', action='store_true')
    parser.add_argument('-c', '--conf', help='YAML config file', required=True)

    args = parser.parse_args()
    conf = OmegaConf.load(args.conf)

    try:
        manager = StreamersManager.from_conf(
            conf_streamers=conf.streamers,
            conf_logs=conf.logs,
            conf_cache=conf.redis,
            conf_broker=conf.kafka
        )

        if args.start:
            manager.start_all()
        elif args.enable:
            manager.enable_all()
        elif args.disable:
            manager.disable_all()
        elif args.interrupt:
            manager.interrupt_all()
        else:
            parser.print_help()
    except KeyboardInterrupt:
        manager.interrupt_all()
