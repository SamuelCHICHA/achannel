from Bot import Bot
import json


# TODO Add image for the bot

def main():
    with open("configuration/private_config.json", "r") as private_config_file:
        token = json.load(private_config_file)["token"]
    with open("configuration/public_config.json", "r") as public_config_file:
        config = json.load(public_config_file)
    bot = Bot(config["prefix"], config["commands"], config["supported_activities"])
    bot.run(token)


if __name__ == '__main__':
    main()
