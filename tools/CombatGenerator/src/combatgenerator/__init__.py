import json
from pathlib import Path
from typing import Dict, List, Union, Optional
from rich import print

from pydantic import BaseModel

combat_path = Path(__file__).parent.parent.parent / "data" / "input.json"
output_path = Path(__file__).parent.parent.parent / "data" / "output.json"
json_template = {
    "recognition": "TemplateMatch",
    "template": "Combat/StopCombat.png",
    "roi": [0, 0, 136, 140],
    "action": "Custom",
    "pre_delay": 0,
    "post_delay": 0,
    "next": [],
}


class Action(BaseModel):
    pre_delay: int
    post_delay: int


class Combat(BaseModel):
    role: str
    version: str
    combat: List


def default_delay(data: str) -> Action:
    """根据动作名称，返回对应的预延迟和后延迟。

    参数:
        data (str): 动作名称

    返回:
        Action: 包含预延迟和后延迟的对象
    """
    movement = [
        "Forward",
        "Backward",
        "Left",
        "Right",
        "Left Forward",
        "Left Backward",
        "Right Forward",
        "Right Backward",
    ]
    qte = ["QTE1", "QTE2"]

    if data in movement:
        return Action(pre_delay=0, post_delay=50)

    elif data == "BasicATK":
        return Action(pre_delay=0, post_delay=200)

    elif data == "BasicATKCharge":
        return Action(pre_delay=0, post_delay=100)

    elif data == "Evade":
        return Action(pre_delay=0, post_delay=150)

    elif data == "Ultimate":
        return Action(pre_delay=0, post_delay=150)

    elif data == "UltimateCharge":
        return Action(pre_delay=0, post_delay=100)

    elif data == "WeaponSkill":
        return Action(pre_delay=0, post_delay=150)

    elif data == "ELFSkill":
        return Action(pre_delay=0, post_delay=150)

    elif data == "ExtraSkill":
        return Action(pre_delay=0, post_delay=100)


def generate_json_from_combat(combat: List) -> Dict:
    """
    根据传入的 "combat" 列表生成对应的 JSON 结构。

    参数:
        combat (List): 包含 "combat" 操作的列表。

    返回:
        dict: 生成的 JSON 对象。
    """
    global json_template
    generated_json = {}
    next_index = 0

    for idx, item in enumerate(combat):
        # 如果 item 是字符串，直接设置 custom_action
        data = json_template.copy()
        if isinstance(item, str):
            data["custom_action"] = item
            delay = default_delay(item)  # 获取默认的 pre_delay 和 post_delay
            data["pre_delay"] = delay.pre_delay
            data["post_delay"] = delay.post_delay

        elif isinstance(item, dict):
            for key, value in item.items():
                data["custom_action"] = key
                if isinstance(value, list) and len(value) == 2:
                    data["pre_delay"] = value[0]
                    data["post_delay"] = value[1]
                else:
                    delay = default_delay(key)  # 这里获取默认延迟
                    data["pre_delay"] = delay.pre_delay
                    data["post_delay"] = delay.post_delay

        # 设置 next 字段
        next_step = f"UniversalMirageCombatGeneric_{str(next_index + 1).zfill(3)}"
        data["next"] = ["UniversalMirageCombatFinish", next_step]

        # 对于第一个元素，特殊处理其名称
        if idx == 0:
            current_step = "UniversalMirageCombatGenericPreheat"
            data["pre_delay"] = 500
            data["post_delay"] = 1500
        else:
            current_step = f"UniversalMirageCombatGeneric_{str(next_index).zfill(3)}"

        # 将新生成的 JSON 对象添加到 generated_json 中
        generated_json[current_step] = data

        # 更新 next_index
        next_index += 1

    if generated_json:
        last_step = f"UniversalMirageCombatGeneric_{str(next_index - 1).zfill(3)}"
        generated_json[last_step]["next"] = ["UniversalMirageCombatFinish"]

    return generated_json


def read_file(path: Path) -> str:
    """读取指定路径的文件内容。

    参数:
        path (Path): 文件路径。

    返回:
        str: 文件内容。
    """
    with open(path, "r") as f:
        return f.read()


def save_file(path: Path, content) -> None:
    """将内容保存到指定路径的文件中。

    参数:
        path (Path): 文件路径。
        content: 要保存的内容。

    返回:
        None
    """
    with open(path, "w") as f:
        json.dump(content, f)


if __name__ == "__main__":
    file = read_file(combat_path)
    print(
        f"角色名{Combat.model_validate_json(file).role}, 版本号{Combat.model_validate_json(file).version}"
    )
    save_file(
        output_path,
        generate_json_from_combat(Combat.model_validate_json(file).combat),
    )
