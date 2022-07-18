import os, json
from fuzzywuzzy import process
from discord import Colour

def find(input_:str):
    objs = []
    aliases = {}
    path = './data/kr/table-data/heroes'
    for obj in os.listdir(path):
        objs.append(str(obj[:-5]))
        with open(f'{path}/{obj}') as f:
            re_ = json.load(f)
            if re_['aliases'] is not None:
                for aliases_ in re_['aliases']:
                    objs.append(aliases_)
                    aliases[aliases_] = obj[:-5]
    re = process.extractOne(input_, objs)
    re_ = re[0]
    try:
        with open(f'./data/kr/table-data/heroes/{re[0]}.json') as f:
            data = json.load(f)
    except:
        with open(f'./data/kr/table-data/heroes/{aliases[re[0]]}.json') as f:
            data = json.load(f)
            re_ = aliases[re[0]]
    return re_, data

def find_boss(input_:str):
    objs = []
    aliases = {}
    path = './data/kr/table-data/bosses'
    for obj in os.listdir(path):
        objs.append(str(obj[:-5]))
        with open(f'{path}/{obj}') as f:
            re_ = json.load(f)
            if re_['aliases'] is not None:
                for aliases_ in re_['aliases']:
                    objs.append(aliases_)
                    aliases[aliases_] = obj[:-5]
    re = process.extractOne(input_, objs)
    re_ = re[0]
    try:
        with open(f'./data/kr/table-data/bosses/{re[0]}.json') as f:
            data = json.load(f)
    except:
        with open(f'./data/kr/table-data/bosses/{aliases[re[0]]}.json') as f:
            data = json.load(f)
            re_ = aliases[re[0]]
    return re_, data

def find_(input_:str):
    objs = []
    aliases = {}
    paths = ['./data/kr/table-data/heroes', './data/kr/table-data/bosses']
    for path in paths:
        for obj in os.listdir(path):
            objs.append(str(obj[:-5]))
            with open(f'{path}/{obj}') as f:
                re_ = json.load(f)
                if re_['aliases'] is not None:
                    for aliases_ in re_['aliases']:
                        objs.append(aliases_)
                        aliases[aliases_] = obj[:-5]
    re = process.extractOne(input_, objs)
    re_ = re[0]
    boss = None
    try:
        with open(f'./data/kr/table-data/heroes/{re[0]}.json') as f:
            data = json.load(f)
    except FileNotFoundError:
        try:
            with open(f'./data/kr/table-data/heroes/{aliases[re[0]]}.json') as f:
                data = json.load(f)
                re_ = aliases[re[0]]
        except:
            try:
                with open(f'./data/kr/table-data/bosses/{re[0]}.json') as f:
                    data = json.load(f)
                    boss = True
            except:
                with open(f'./data/kr/table-data/bosses/{aliases[re[0]]}.json') as f:
                    data = json.load(f)
                    re_ = aliases[re[0]]
                    boss = True
    except:
        pass
    return re_, data, boss

def get_color(cls):
    if cls == 'wizard':
        clr = Colour.from_rgb(123, 0, 0)
    elif cls == 'warrior':
        clr = Colour.from_rgb(123, 60, 0)
    elif cls == 'knight':
        clr = Colour.from_rgb(26, 63, 112)
    elif cls == 'assassin':
        clr = Colour.from_rgb(118, 0, 102)
    elif cls == 'archer':
        clr = Colour.from_rgb(51, 116, 0)
    elif cls == 'mechanic':
        clr = Colour.from_rgb(0, 20, 122)
    elif cls == 'priest':
        clr = Colour.from_rgb(0, 101, 115)

    elif cls == 'tyrfas':
        clr = Colour.from_rgb(105, 145, 170)
    elif cls == 'lakreil':
        clr = Colour.from_rgb(199, 170, 126)
    elif cls == 'velkazar':
        clr = Colour.from_rgb(194, 70, 70)
        
    elif cls == 'xakios':
        clr = Colour.from_rgb(71, 181, 83)
    elif cls == 'nordik':
        clr = Colour.from_rgb(27, 24, 92)
    elif cls == 'nubis':
        clr = Colour.from_rgb(180, 122, 71)
    elif cls == 'gushak':
        clr = Colour.from_rgb(157, 65, 54)
    elif cls == 'maviel':
        clr = Colour.from_rgb(60, 4, 9)
    elif cls == 'manticore':
        clr = Colour.from_rgb(139, 71, 13)

    elif cls == 'mountain fortress':
        clr = Colour.from_rgb(182, 150, 113)
    elif cls == 'protianus' or cls == 'event protianus':
        clr = Colour.from_rgb(69, 103, 179)
    elif cls == 'xanadus':
        clr = Colour.from_rgb(75, 36, 100)

    elif cls == 'imet':
        clr = Colour.from_rgb(250, 66, 44)
    elif cls == 'musama':
        clr = Colour.from_rgb(185, 60, 150)
    elif cls == 'sekmaha':
        clr = Colour.from_rgb(5, 164, 251)

    elif cls == 'devourer shakmeh':
        clr = Colour.from_rgb(0, 0, 0)
    elif cls == 'otherworldly shakmeh':
        clr = Colour.from_rgb(26, 53, 215)

    elif cls == 'galgoria' or cls == 'siegfried' or cls == 'ascalon':
        clr = Colour.from_rgb(200,181,164)

    elif cls == 'tersio' or cls == 'apocalypsion':
        clr = Colour.from_rgb(80,72,109)

    else:
        clr = config.embed_color
    return clr