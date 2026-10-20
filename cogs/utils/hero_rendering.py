"""Shared hero and boss embed rendering."""
import discord
from .find_obj import get_color
from .menus import asset

class HeroRendering:
    get_color = staticmethod(get_color)

    def get_infos(self, obj, data, boss=None):
        clr = self.get_color(data['infos']['class'].lower())
        des = ''
        if boss:
            for info in data['infos']:
                if info == 'thumbnail':
                    continue
                elif info == 'class':
                    continue
                else:
                    des+='**'+info.title()+'**: '+data['infos'][info]+'\n'
        else:
            for info in data['infos']:
                if info == 'thumbnail':
                    continue
                elif info == 'story':
                    des+='\n**Story**'+'\n'+data['infos'][info]
                elif info == 'story_':
                    pass
                else:
                    des+='**'+info.title()+'**: '+data['infos'][info]+'\n'
        embed = discord.Embed(
            title=obj + ' Infos',
            description=des,
            colour=clr,
        )
        name = f'{obj}_ico.png'
        if ' ' in name:
            name = name.replace(' ', '_')
        file = asset(data['infos']['thumbnail'], filename=name)
        embed.set_thumbnail(url=f'attachment://{name}')
        return embed, file

    def get_skills(self, obj, data, boss=None):
        clr = self.get_color(data['infos']['class'].lower())
        des = ''
        embeds = []
        for page in data['skills']:
            if page.startswith('page'):
                for skill in data['skills'][page]:
                    try:
                        try:
                            des+=('**Skill '+skill+': '+data['skills'][page][skill]['name']+' [Cost: '+
                                data['skills'][page][skill]['cost']+'] [Cooldown: '+data['skills'][page][skill]['cooldown']+']**\n'+
                                data['skills'][page][skill]['description']+'\n\n')
                        except:
                            des+=('**Skill '+skill+': '+data['skills'][page][skill]['name']+' [Cooldown: '+data['skills'][page][skill]['cooldown']+']**\n'+
                                data['skills'][page][skill]['description']+'\n\n')
                    except:
                        des+=('**Skill '+skill+': '+data['skills'][page][skill]['name']+'**\n'+
                            data['skills'][page][skill]['description']+'\n\n')
                embed = discord.Embed(
                    title=obj + ' Skills (' + page.title() + ')',
                    description=des,
                    colour=clr,
                    )
                embeds.append(embed)
                des = ''
            else:
                for skill in data['skills']:
                    try:
                        des+=('**Skill '+skill+': '+data['skills'][skill]['name']+' [Cost: '+
                            data['skills'][skill]['cost']+'] [Cooldown: '+data['skills'][skill]['cooldown']+']**\n'+
                            data['skills'][skill]['description']+'\n\n')
                    except:
                        des+=('**Skill '+skill+': '+data['skills'][skill]['name']+'**\n'+
                            data['skills'][skill]['description']+'\n\n')
                embed = discord.Embed(
                    title=obj + ' Skills',
                    description=des,
                    colour=clr,
                )
                embeds.append(embed)
                break
        count = 0
        if len(embeds) >= 2:
            for embed in embeds:
                embeds[count].set_footer(text=f'Page {count+1}/{len(embeds)}')
                count+=1
        return embeds

    def get_books(self, obj, data):
        clr = self.get_color(data['infos']['class'].lower())
        des = ''
        for book in data['books']:
            des+='**Skill '+book+'**\n'
            for upgrade in data['books'][book]:
                des+='[UPGRADE '+upgrade+'] '+data['books'][book][upgrade]+'\n'
            des+='\n'
        embed = discord.Embed(
            title=obj + ' Books',
            description=des,
            colour=clr,
        )
        return embed

    def get_class_perk(self, cls, clr):
        des = '**T1 Perks**\n'
        with open(f'./data/kr/table-data/classes/General.json') as f:
            t1 = json.load(f)['perks']['t1']
        for perk in t1:
            des+='**'+perk+'**\n'+t1[perk]+'\n'
        des+='\n**T2 Perks**\n'
        with open(f'./data/kr/table-data/classes/{cls}.json') as f:
            t2 = json.load(f)['perks']['t2']
        for perk in t2:
            des+='**'+perk+'**\n'+t2[perk]+'\n' 
        embed = discord.Embed(
            title=cls + ' Perks',
            description=des,
            colour=clr,
        )
        return embed, des

    def get_uw(self, obj, data, stars:int=None):
        clr = self.get_color(data['infos']['class'].lower())
        des = ''
        des = data['uw']['name']+'\n\n'+data['uw']['description']+'\n\n'
        if stars is not None:
            des = '☆☆☆☆☆'.replace('☆', '★', stars)+'\n'+des
            for value in data['uw']['value']:
                des = des.replace(f'({value})', data['uw']['value'][value][str(stars)], 1)
        else:
            for value in data['uw']['value']:
                des+='('+value+'): '
                for vl in data['uw']['value'][value]:
                    des+=data['uw']['value'][value][vl]+', '
                des=des[:-2]+'\n'
        embed = discord.Embed(
            title=obj + ' UW',
            description=des,
            colour=clr,
        )
        name = f'{obj}_uw.png'
        if ' ' in name:
            name = name.replace(' ', '_')
        file = asset(data['uw']['thumbnail'], filename=name)
        embed.set_thumbnail(url=f'attachment://{name}')
        return embed, file

    def get_sw(self, obj, data):
        clr = self.get_color(data['infos']['class'].lower())
        des = ''
        des = '**Requirement**: '+data['sw']['requirement']+'\n\n'+data['sw']['description']
        for adv in data['sw']['advancement']:
            des+='\n\n**Advancement '+adv+'**\n'+data['sw']['advancement'][adv]
        embed = discord.Embed(
            title=obj + ' SW',
            description=des,
            colour=clr,
        )
        embed.set_footer(text=f"Cooldown: {data['sw']['cooldown']} | Uses: {data['sw']['uses']}")
        file = None
        try:
            name = f'{obj}_sw.png'
            if ' ' in name:
                name = name.replace(' ', '_')
            file = asset(data['sw']['thumbnail'], filename=name)
            embed.set_thumbnail(url=f'attachment://{name}')
        except:
            pass
        return embed, file

    def get_sa_vs(self, obj, data, cate):
        clr = self.get_color(data['infos']['class'].lower())
        embed = discord.Embed(
            title=obj + ' ' + cate.title(),
            colour=clr,
        )
        name = f'{obj}_{cate}.png'
        if ' ' in name:
            name = name.replace(' ', '_')
        file = asset(data[cate], filename=name)
        embed.set_image(url=f'attachment://{name}')
        return embed, file
