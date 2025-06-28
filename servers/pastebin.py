import logging
import requests
import xmltodict
import os

from typing import Literal
from dotenv import load_dotenv
from mcp.server import FastMCP

load_dotenv()


def getEnv(key: str, default: str | None = None) -> str:
    value = os.getenv(key, default)

    if value is None:
        raise ValueError(f"Environment variable {key} not found")

    return value


api_key = getEnv("API_DEV_KEY")
user_key = getEnv("API_USER_KEY")

mcp = FastMCP("Personal MCP Tools")
logger = logging.getLogger(__name__)


class PastebinWrapper:
    EXPIRATION_VALUES = Literal[
        "10M",  # 10 minutes
        "1H",  # 1 hour
        "1D",  # 1 day
        "1W",  # 1 week
        "2W",  # 2 weeks
        "1M",  # 1 month
        "1Y",  # 1 year
        "N",  # Never expire
    ]
    __BASEURL = "https://pastebin.com/api"
    __API_DEV = None
    __USER_DEV = None

    def __init__(self, api_key: str | None, user_key: str | None):
        self.__API_DEV = api_key
        self.__USER_DEV = user_key

    def get_userinfo(self):
        logger.info("Getting user info...")

        response = requests.post(
            url=f"{PastebinWrapper.__BASEURL}/api_post.php",
            data={
                "api_dev_key": self.__API_DEV,
                "api_user_key": self.__USER_DEV,
                "api_option": "userdetails",
            },
        )

        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code} - {response.text}")

        userinfo_dict = xmltodict.parse(response.text)

        logger.info(f"User info: {userinfo_dict}")

        return userinfo_dict

    def create_paste(
        self,
        text: str,
        title: str = "Untitled",
        privacy: int = 0,
        duration: EXPIRATION_VALUES = "N",
    ):
        logger.info(f"Creating paste with title '{title}'...")
        body = {
            "api_dev_key": self.__API_DEV,
            "api_user_key": self.__USER_DEV,
            "api_option": "paste",
            "api_paste_expire_date": duration,
            "api_paste_code": text,
            "api_paste_name": title,
            "api_paste_private": privacy,
        }
        response = requests.post(
            url=f"{PastebinWrapper.__BASEURL}/api_post.php", data=body
        )

        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code} - {response.text}")

        logger.info(f"Paste created with URL: {response.text}")

        return response.text

    @staticmethod
    def generate_userkey(api_key: str, username: str, password: str):
        logger.info(f"Generating user key for {username}...")

        response = requests.post(
            url=f"{PastebinWrapper.__BASEURL}/api_login.php",
            data={
                "api_dev_key": api_key,
                "api_user_name": username,
                "api_user_password": password,
            },
        )

        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code} - {response.text}")

        logger.info(f"User key {response.text} generated for {username}.")

        return response.text


# Create an instance of the PastebinWrapper class
pastebin = PastebinWrapper(api_key=api_key, user_key=user_key)


@mcp.resource(
    uri="helper://expiration_values",
    name="pastebin_expire_time_values",
    description="can_be: 10M, 1H, 1D, 1W, 2W, 1M, 1Y",
)
def pastebin_expire_time_values() -> str:
    return """
    10M: 10 Minutes
    1H: 1 Hour
    1D: 1 Day
    1W: 1 Week
    2W: 2 Weeks
    1M: 1 Month
    1Y: 1 Year
    N: Never
    """


@mcp.tool(
    name="pastebin_paste_creation_tool",
    description="pastebin_create_paste",
)
def pastebin_create_paste(
    text: str,
    title: str = "Untitled",
    privacy: int = 0,
    duration: PastebinWrapper.EXPIRATION_VALUES = "N",
) -> str:
    try:
        paste_url = pastebin.create_paste(
            text=text,
            title=title,
            privacy=privacy,
            duration=duration,
        )
        return "Created paste with URL: " + paste_url
    except Exception as e:
        return f"A exeception ocurred: {e}"


@mcp.tool(
    name="pastebin_userinfo_tool",
    description="Get pastebin user info like eg. API_KEY, USER_KEY, USER_NAME, EMAIL, ACCOUNT_TYPE, PRO_EXPIRATION",
)
def pastebin_userinfo() -> str:
    try:
        userinfo = pastebin.get_userinfo()
        if userinfo.get("user"):
            userinfo = userinfo["user"]
        else:
            return "User not found"

        return f"""
        Api Key: {api_key}
        User Key: {user_key}
        Username: {userinfo.get("user_name", "N/A")}
        Email: {userinfo.get("user_email", "N/A")}
        Account Type: {userinfo.get("user_account_type", "N/A")} [0=Normal, 1=Pro, N/A=Empty]
        Pro Expiration: {userinfo.get("user_expiration", "N/A")} [N=Never, N/A=Empty]
        """
    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")

