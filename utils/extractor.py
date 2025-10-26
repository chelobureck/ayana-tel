import re
from typing import Dict, Any


def extract_child_info(text: str) -> Dict[str, Any]:
    """
    Простейший извлекатель по шаблонам. На вход — текст сообщений (строка).
    Ищет шаблоны:
      - имя: "имя: <Name>" или "name: <Name>"
      - возраст: "возраст: 5", "age: 5 лет", "5 лет"
      - аллергия: "аллерг(ия|и): ..."
    Возвращает словарь с найденными полями.
    """
    out: Dict[str, Any] = {}
    s = text.lower()

    # name
    m = re.search(r"(?:имя|name)[:\s]+([А-Яа-яA-Za-z\-']{2,40})", text)
    if m:
        out["name"] = m.group(1).strip()

    # age digits
    m = re.search(r"([0-9]{1,2})\s*(?:лет|года|год|y/o|age)", s)
    if m:
        try:
            out["age"] = int(m.group(1))
        except ValueError:
            pass

    # allergies
    m = re.search(r"(?:аллерг(?:ия|ии)|allerg(?:y|ies))[:\s]+([^\n,;]+)", text, re.I)
    if m:
        out.setdefault("additional", {})
        out["additional"]["allergies"] = m.group(1).strip()

    # simple heuristics: "рождён(а) в", "дата рождения" etc. (add later)
    return out