from Bot import Bot
import json


def main():
    with open("config.json", "r") as config_file:
        config = json.load(config_file)
    bot = Bot(config["prefix"])
    bot.run(config["token"])


if __name__ == '__main__':
    main()
