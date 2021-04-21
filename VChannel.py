import random
from Data import Data
import sys


class VChannel:
    def __init__(self):
        self.among_us_voice_channel_names = VChannel.get_voice_channel_names(Data.Files.AMONG_US_NAMES_FILE_PATH)
        self.general_voice_channel_names = VChannel.get_voice_channel_names()

    @staticmethod
    def get_voice_channel_names(file_path: str = Data.Files.GENERAL_NAMES_FILE_PATH) -> list[str]:
        voice_channel_names = []
        if not isinstance(file_path, str):
            raise TypeError("Expecting a string.")
        if file_path not in Data.Files.__dict__.values():
            print("No file matching this path, general one is given.", file=sys.stderr)
            file_path = Data.Files.GENERAL_NAMES_FILE_PATH
        with open(file_path, "r") as file:
            for voice_channel_name in file:
                voice_channel_names.append(voice_channel_name)
        return voice_channel_names

    @staticmethod
    def get_voice_channel_name(voice_channel_names: list) -> str:
        if not isinstance(voice_channel_names, list):
            raise TypeError("Expecting a list of string")
        rd_index = random.randint(0, len(voice_channel_names) - 1)
        return voice_channel_names[rd_index]
