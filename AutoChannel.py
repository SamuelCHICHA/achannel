class AutoChannel:
    def __init__(self, supported_activity: dict[str]):
        if not isinstance(supported_activity, dict):
            raise TypeError("Expects a dict.")
        self.supported_activity = dict()
        self.name = supported_activity["name"]
        self.voice_channel_names = AutoChannel.get_voice_channel_names(supported_activity["file_path"])

    @staticmethod
    def get_voice_channel_names(file_path: str) -> list[str]:
        voice_channel_names = []
        if not isinstance(file_path, str):
            raise TypeError("Expecting a string.")
        with open(file_path, "r") as file:
            for voice_channel_name in file:
                voice_channel_names.append(voice_channel_name)
        return voice_channel_names
