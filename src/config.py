

import pytoml as toml

from defines import *
from actions import *
import os

class Config:

    def __init__(self, filename):
        """
        self.filename is the toml file for start
        """
        if not os.path.isfile(filename):
            print("Bad config file")

        abspath = os.path.abspath(filename)
        
        self.filename = os.path.basename(abspath)
        self.path = os.path.dirname(abspath)
        self.tomls = dict()
        self.toml_files = []
        self.toml_config = None
        self.status = ConfigState_Init
        

    def load(self):
        self.__parse_start_toml_files()


    def __parse_start_toml_files(self):

        path = os.path.dirname(os.path.abspath(self.filename))
        
        self.__parse_toml_files([self.filename])
        # print(self.tomls)
        self.status = ConfigState_Parsed

        self.toml_config = self.__load_toml_files()
        # print(self.toml_config)
        self.status = ConfigState_Loaded

    #
    def __parse_toml_files(self, toml_files):
        """
        Parse the toml files, especially against the 'requires'
        """
        for toml_file in toml_files:
            toml_file_path = os.path.join(self.path, toml_file)
            if toml_file_path in self.tomls:
                # Prevent loop require
                continue

            with open(toml_file_path, 'rb') as file:
                # tomls hold all the configs parsed from toml file.
                try:
                    toml_config = toml.load(file)
                except toml.TomlError as e:
                    print(e, "Something goes wrong?")
                    exit(0)

                self.toml_files.append(toml_file_path)
                self.tomls[toml_file_path] = toml_config
                
                if Kw_Requires in toml_config:
                    toml_files = toml_config[Kw_Requires]
                    self.__parse_toml_files(toml_files)

    def __load_toml_files(self):
        """

        """
        result = dict()
        for filename in self.toml_files:
            config = self.tomls[filename]
            self.__merge_dict(result, config)
        return result

    @staticmethod
    def __merge_dict(d1: dict, d2: dict):
        """
        Merge d2 into d1
        """
        for key, value in d2.items():
            if key == '__filename__':
                continue
            if key not in d1:
                d1[key] = value
            else:
                d1[key].update(value)

    def get_pipelines(self):
        actions_map = self.get_value('action')
        
        start_action_names = []
        for action_name, action in actions_map.items():
            if Kw_Start_At in action:
                start_action_names.append(action_name)
        
        if len(start_action_names) == 0:
            print("No start action")
            exit(0)

        pipelines = dict()
        
        for start_action_name in start_action_names:
            # in a pipeline, an action exists once only.
            pipeline = self.get_pipeline(start_action_name)            
            pipelines[start_action_name] = pipeline
        return pipelines

    def get_pipeline(self, start_action_name: str):
        pipeline = dict()
        actions_map = self.get_value('action')
        action_name = start_action_name
        while action_name:
            if action_name in pipeline:
                # loop actions NOT support now.
                break
            pipeline[action_name] = actions_map[action_name]
            action_name = self.get_value('action.%s.next' % action_name)
        
        return pipeline


    @staticmethod
    def get_start_action_name(pipeline: dict) -> BaseAction:
        for action_name, action in pipeline.items():
            if 'start_at' in action:
                return action_name
        return None

    @staticmethod
    def get_action_config(pipeline: dict, action_name: str) -> dict:
        if action_name in pipeline:
            return pipeline[action_name]
        else:
            return None

    def get_value(self, key, default_val=None):
        if "." not in key:
            # Optimize
            if key in self.toml_config:
                return self.toml_config[key]
            else:
                return default_val
        key_parts = key.split(".")
        return Config.__get_value(self.toml_config, key_parts, default_val)

    @staticmethod
    def __get_value(config_dict, key_parts, default_val):
        config = config_dict
        for key_part in key_parts:
            if key_part in config:
                config = config[key_part]
            else:
                return default_val
        return config


    def __load_resources(self):
        pass

    def __load_resources(self):
        pass        



