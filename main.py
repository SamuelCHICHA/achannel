from Bot import Bot
import json


def main():
    bot = Bot()
    with open("config.json", "r") as config_file:
        loaded_json = json.load(config_file)
    bot.run(loaded_json["token"])


if __name__ == '__main__':
    main()
