'''
The code provides a command-line interface for managing and controlling the 
streaming process for multiple streamers based on the provided configurations and 
user-specified actions.

The code takes command-line arguments to determine the action to be performed. The available 
actions are:

-s or --start: Starts streaming for all streamers.
-e or --enable: Enables streaming for all streamers.
-d or --disable: Disables streaming for all streamers.
-i or --interrupt: Interrupts streaming for all streamers.
The code reads the YAML configuration file specified through the -c or --conf argument. 
This configuration file contains the necessary configurations for the streamers, logs, cache, 
and broker.

By using the StreamersManager class and the provided configurations, the code executes the 
specified action for all streamers. If none of the valid arguments is provided or if an 
interruption occurs (KeyboardInterrupt), the code handles the situation accordingly.

The module can be used as follows:
pip install omegaconf
python streaming_manager.py -c config.yaml -<action>
python streaming_manager.py -c config.yaml -s

'''
import os
import argparse
from omegaconf import OmegaConf
from streamers_manager import StreamersManager

if __name__ == '__main__':
    #Create an ArgumentParser object to handle command-line arguments
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-s', '--start', help='Start streaming', action='store_true')
    group.add_argument('-e', '--enable', help='Enable streaming', action='store_true')
    group.add_argument('-d', '--disable', help='Disable streaming', action='store_true')
    group.add_argument('-i', '--interrupt', help='Interrupt streaming', action='store_true')
    parser.add_argument('-c', '--conf', help='YAML config file', required=True)

    #Parse the command-line arguments
    args = parser.parse_args()
    
    #Load the YAML configuration file
    conf = OmegaConf.load(args.conf)

    try:
        #Create an istance of the StreamersManager using the provided configurations
        manager = StreamersManager.from_conf(
            conf_streamers=conf.streamers,
            conf_logs=conf.logs,
            conf_cache=conf.redis,
            conf_broker=conf.kafka
        )
        
        # Perform the specified action based on the command-line arguments
        if args.start:
            manager.start_all() #Start Streaming for all streamers
        elif args.enable:
            manager.enable_all() #Enable streaming for all streamers
        elif args.disable:
            manager.disable_all() #Disable streaming for all streamers
        elif args.interrupt:
            manager.interrupt_all() #Interrupt streaming for all streamers 
        else:
            parser.print_help() #Print help message if no valid argument is provided
    except KeyboardInterrupt:
        manager.interrupt_all() #Interrupt all streamers in case of a KeyboardInterrupt 
