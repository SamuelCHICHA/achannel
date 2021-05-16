import json
import sys
from typing import Optional
import logging
import requests

BASE_URL = "http://localhost:3000"
TIMEOUT = 0.5


async def register_guild(guild_id: int) -> bool:
    data = {"guild_id": guild_id}
    raw_res = None
    try:
        raw_res = requests.post(f"{BASE_URL}/register-guild", json=data, timeout=TIMEOUT)
    except Exception as e:
        logging.critical(e)
    if raw_res:
        if raw_res.status_code == 200:
            res = json.loads(raw_res.content)
            return res["status"] == 0
        else:
            logging.warning(f"Communication with API failed: [{raw_res.status_code}]: {raw_res.content}")


async def get_voice_channel_name(guild_id: int, activity: str) -> Optional[str]:
    raw_res = None
    try:
        raw_res = requests.get(f"{BASE_URL}/guild/{guild_id}/activity/{activity.lower()}/random-channel-name",
                               timeout=TIMEOUT)
    except Exception as e:
        logging.critical(e)
    if raw_res:
        if raw_res.status_code == 200:
            res = json.loads(raw_res.content)
            if res["status"] == 0:
                return res["content"]
            elif res["status"] == 3:
                print(f"No channel names for activity {activity} in guild {guild_id}.")
            else:
                print(f"Could not retrieve channel name for the activity {activity} in the guild {guild_id} from api.",
                      file=sys.stderr)
                print(f"API response: {res}")
        else:
            logging.warning(f"Communication with API failed: [{raw_res.status_code}]: {raw_res.content}")


async def get_voice_channel_names(guild_id: int, activity: str) -> Optional[list[str]]:
    raw_res = None
    try:
        raw_res = requests.get(f"{BASE_URL}/guild/{guild_id}/activity/{activity.lower()}/channel-names",
                               timeout=TIMEOUT)
    except Exception as e:
        logging.critical(e)
    if raw_res:
        if raw_res.status_code == 200:
            res = json.loads(raw_res.content)
            if res["status"] == 0:
                return res["content"]
            elif res["status"] == 3:
                print(f"No channel names for activity {activity} in guild {guild_id}.")
            else:
                print(f"Could not retrieve channel names for the activity {activity} in the guild {guild_id} from api.",
                      file=sys.stderr)
                print(f"API response: {res}", file=sys.stderr)
        else:
            logging.warning(f"Communication with API failed: [{raw_res.status_code}]: {raw_res.content}")


async def register_voice_channel_names(guild_id: int, activity: str, channel_names: list[str]) -> bool:
    data = {"channel_names": [cn.lower().strip() for cn in channel_names]}
    raw_res = None
    try:
        raw_res = requests.post(f"{BASE_URL}/guild/{guild_id}/activity/{activity}/register-channel-name", json=data,
                                timeout=TIMEOUT)
    except Exception as e:
        logging.critical(e)
    if raw_res:
        if raw_res.status_code == 200:
            res = json.loads(raw_res.content)
            return res["status"] == 0
        else:
            logging.warning(f"Communication with API failed: [{raw_res.status_code}]: {raw_res.content}")


async def register_activities(guild_id: int, activities: list[str]) -> bool:
    data = {"activities": [ac.lower().strip() for ac in activities]}
    raw_res = None
    try:
        raw_res = requests.post(f"{BASE_URL}/guild/{guild_id}/register-activity", json=data, timeout=TIMEOUT)
    except Exception as e:
        logging.critical(e)
    if raw_res:
        if raw_res.status_code == 200:
            res = json.loads(raw_res.content)
            print(res)
            return res["status"] == 0
        else:
            logging.warning(f"Communication with API failed: [{raw_res.status_code}]: {raw_res.content}")


async def get_activities(guild_id: int) -> Optional[list[str]]:
    raw_res = None
    try:
        raw_res = requests.get(f"{BASE_URL}/guild/{guild_id}/activities", timeout=TIMEOUT)
    except Exception as e:
        logging.error(e)
    if raw_res:
        if raw_res.status_code == 200:
            res = json.loads(raw_res.content)
            if res["status"] == 0:
                return res["content"]
            elif res["status"] == 3:
                print(f"No activities for guild {guild_id}.")
            else:
                print(f"Could not retrieve activities for guild {guild_id} from api.", file=sys.stderr)
                print(f"API response: {res}", file=sys.stderr)
        else:
            logging.warning(f"Communication with API failed: [{raw_res.status_code}]: {raw_res.content}")


async def delete_guild(guild_id: int) -> bool:
    data = {"guild_id": guild_id}
    raw_res = None
    try:
        raw_res = requests.post(f"{BASE_URL}/delete-guild", json=data, timeout=TIMEOUT)
    except Exception as e:
        logging.critical(e)
    if raw_res:
        if raw_res.status_code == 200:
            res = json.loads(raw_res.content)
            return res["status"] == 0
        else:
            logging.warning(f"Communication with API failed: [{raw_res.status_code}]: {raw_res.content}")


async def delete_activities(guild_id: int, activities: list[str]) -> bool:
    data = {"activities": activities}
    raw_res = None
    try:
        raw_res = requests.post(f"{BASE_URL}/guild/{guild_id}/delete-activities", json=data, timeout=TIMEOUT)
    except Exception as e:
        logging.critical(e)
    if raw_res:
        if raw_res.status_code == 200:
            res = json.loads(raw_res.content)
            print(res)
            return res["status"] == 0
        else:
            logging.warning(f"Communication with API failed: [{raw_res.status_code}]: {raw_res.content}")
