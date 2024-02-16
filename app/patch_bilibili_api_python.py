from bilibili_api import Credential, login_func
from bilibili_api.login_func import QrCodeLoginEvents
from bilibili_api.exceptions import LoginError
from bilibili_api import login
from typing import Tuple, Union

def patch_check_qrcode_events(login_key: str) -> Tuple[QrCodeLoginEvents, Union[str, Credential]]:
    """
    检查登录状态。（建议频率 1s，这个 API 也有风控！）

    Args:
        login_key (str): 登录密钥（get_qrcode 的返回值第二项)

    Returns:
        Tuple[QrCodeLoginEvents, str|Credential]: 状态(第一项）和信息（第二项）（如果成功登录信息为凭据类）
    """
    events = login.login_with_key(login_key)

    if events["code"] == 86101:
        return login_func.QrCodeLoginEvents.SCAN, events["message"]
    elif events["code"] == 86090:
        return login_func.QrCodeLoginEvents.CONF, events["message"]
    elif events["code"] == 86038:
        return login_func.QrCodeLoginEvents.TIMEOUT, events["message"]
    elif events["code"] == 0:
        url: str = events["url"]
        cookies_list = url.split("?")[1].split("&")
        sessdata = ""
        bili_jct = ""
        dede = ""
        for cookie in cookies_list:
            if cookie[:8] == "SESSDATA":
                sessdata = cookie[9:]
            if cookie[:8] == "bili_jct":
                bili_jct = cookie[9:]
            if cookie[:11].upper() == "DEDEUSERID=":
                dede = cookie[11:]
        c = Credential(sessdata, bili_jct, dedeuserid=dede)
        return login_func.QrCodeLoginEvents.DONE, c
    else:
        raise LoginError(events["message"])