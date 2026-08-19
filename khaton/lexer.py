from __future__ import annotations
import shlex

COMMANDS = ('let','const','printty','input','if','Deli','else','end','repeat','while','fn','return','call','import','match','case','break','continue','assert','type','struct','enum','new','delete','set','get','add','sub','mul','div','mod','eq','lt','gt','and','or','not','emit','sleep','try','args')

def lex(line: str) -> list[str]:
    return shlex.split(line, comments=True, posix=True)

def is_command(word: str) -> bool: return word in COMMANDS
