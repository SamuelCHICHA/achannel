import json
import logging

from Bot import Bot


# TODO delete auto-channel on deletion of the associated voice channel
# TODO add roles with a string instead of the mention ?

def main():
    logging.basicConfig(
        filename="bot.log",
        filemode="w",
        encoding="utf-8",
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] %(module)s/%(funcName)s: %(message)s",
        datefmt="%Y/%m/%d %H:%M:%S"
    )
    with open("bot_config.json", "r") as config_file:
        config = json.load(config_file)
    bot = Bot(
        prefix=config["prefix"],
        description=config["description"],
        good_reaction=config["good_reaction"],
        bad_reaction=config["bad_reaction"],
        mother_category=config["category"]
    )
    bot.run()


if __name__ == '__main__':
    main()
