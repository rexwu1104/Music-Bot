import json

from typing import Literal

class Translator:
    __guild_key: dict[int, dict[str, str]] = {}
    __translate_data: dict[str, dict[str, str]] = {}
    
    @classmethod
    def init(cls, *keys: list[str]):
        for key in keys:
            with open(f'./modules/translator/i18n/{key}.json', 'r', encoding='utf-8') as tfile:
                cls.__translate_data[key] = json.load(tfile)
    
    @classmethod
    def __get_data(cls, id: int) -> dict[str, str]:
        return cls.__guild_key[id]
    
    @classmethod
    def translate(cls, id: int, content: str) -> str:
        return cls.__get_data(id).get(content, '')
    
    @classmethod
    def register(cls, id: int, type: Literal['en-us', 'zh-tw'] = None):
        if type is None:
            type = 'zh-tw'
            
        cls.__guild_key[id] = cls.__translate_data[type]