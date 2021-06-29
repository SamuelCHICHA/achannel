import json
import logging
from typing import Optional

import requests

BASE_URL = "http://localhost:3000"
TIMEOUT = 0.5


async def register_guild(guild_id: int) -> Optional[int]:
    data = {"guild_id": guild_id}
    tmp(data)
    raw_res = requests.post(
        f"{BASE_URL}/register-guild",
        json=data,
        timeout=TIMEOUT
    )
    if raw_res:
        if raw_res.status_code == 200:
            res = json.loads(raw_res.content)
            if res["status"] == 1:
                raise Exception(res["content"])
            elif res["status"] == 0:
                return res["content"]
        else:
            raw_res.raise_for_status()


async def get_voice_channel_name(guild_id: int, activity: str) -> Optional[str]:
    tmp(guild_id, activity)
    raw_res = requests.get(
        f"{BASE_URL}/guild/{guild_id}/activity/{activity.lower()}/random-channel-name",
        timeout=TIMEOUT
    )
    if raw_res:
        if raw_res.status_code == 200:
            res = json.loads(raw_res.content)
            if res["status"] == 1:
                raise Exception(res["content"])
            elif res["status"] == 0:
                return res["content"]
            elif res["status"] == 3:
                logging.warning(f"No channel names for activity {activity} in guild {guild_id}.")
        else:
            raw_res.raise_for_status()


async def get_voice_channel_names(guild_id: int, activity: str) -> Optional[list[str]]:
    tmp(guild_id, activity)
    raw_res = requests.get(
        f"{BASE_URL}/guild/{guild_id}/activity/{activity.lower()}/channel-names",
        timeout=TIMEOUT
    )
    if raw_res:
        if raw_res.status_code == 200:
            res = json.loads(raw_res.content)
            if res["status"] == 1:
                raise Exception(res["content"])
            elif res["status"] == 0:
                return res["content"]
            elif res["status"] == 3:
                logging.warning(f"No channel names for activity {activity} in guild {guild_id}.")
        else:
            raw_res.raise_for_status()


async def register_voice_channel_names(guild_id: int, activity: str, channel_names: list[str]) -> Optional[int]:
    data = {"channel_names": [cn.lower().strip() for cn in channel_names]}
    tmp(guild_id, data)
    raw_res = requests.post(
        f"{BASE_URL}/guild/{guild_id}/activity/{activity}/register-channel-name",
        json=data,
        timeout=TIMEOUT
    )
    if raw_res:
        if raw_res.status_code == 200:
            res = json.loads(raw_res.content)
            if res["status"] == 1:
                raise Exception(res["content"])
            elif res["status"] == 0:
                return res["content"]
        else:
            raw_res.raise_for_status()


async def register_activities(guild_id: int, activities: list[str]) -> Optional[int]:
    data = {"activities": [ac.lower().strip() for ac in activities]}
    tmp(guild_id, data)
    raw_res = requests.post(
        f"{BASE_URL}/guild/{guild_id}/register-activity",
        json=data,
        timeout=TIMEOUT
    )
    if raw_res:
        if raw_res.status_code == 200:
            res = json.loads(raw_res.content)
            if res["status"] == 1:
                raise Exception(res["content"])
            elif res["status"] == 0:
                return res["content"]
        else:
            raw_res.raise_for_status()


async def get_activities(guild_id: int) -> Optional[list[str]]:
    tmp(guild_id)
    raw_res = requests.get(
        f"{BASE_URL}/guild/{guild_id}/activities",
        timeout=TIMEOUT
    )
    if raw_res:
        if raw_res.status_code == 200:
            res = json.loads(raw_res.content)
            if res["status"] == 0 or res["status"] == 3:
                if res["status"] == 3:
                    logging.info(f"No activities for guild {guild_id}.")
                return res["content"]
            elif res["status"] == 1:
                raise Exception(res["content"])
        else:
            raw_res.raise_for_status()


async def delete_guild(guild_id: int) -> Optional[int]:
    data = {"guild_id": guild_id}
    tmp(data)
    raw_res = requests.post(
        f"{BASE_URL}/delete-guild",
        json=data,
        timeout=TIMEOUT
    )
    if raw_res:
        if raw_res.status_code == 200:
            res = json.loads(raw_res.content)
            if res["status"] == 1:
                raise Exception(res["content"])
            elif res["status"] == 0:
                return res["content"]
        else:
            raw_res.raise_for_status()


async def delete_activities(guild_id: int, activities: list[str]) -> Optional[int]:
    data = {"activities": activities}
    tmp(guild_id, data)
    raw_res = requests.post(
        f"{BASE_URL}/guild/{guild_id}/delete-activities",
        json=data,
        timeout=TIMEOUT
    )
    print(raw_res.url)
    if raw_res:
        if raw_res.status_code == 200:
            res = json.loads(raw_res.content)
            if res["status"] == 1:
                raise Exception(res["content"])
            elif res["status"] == 0:
                return res["content"]
        else:
            raw_res.raise_for_status()


def tmp(*args):
    for arg in args:
        print(arg)
