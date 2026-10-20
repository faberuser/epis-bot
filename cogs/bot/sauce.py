import asyncio
import logging
import re
import time
from itertools import cycle
from urllib import parse

import cloudscraper
import discord
import requests
from bs4 import BeautifulSoup, Tag
from discord.ext import commands
from lxml.html import fromstring

import settings

PREVIEW_ERRORS = (
    requests.RequestException,
    ValueError,
    TypeError,
    IndexError,
    KeyError,
    AttributeError,
    StopIteration,
)


class Sauce(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.hybrid_command(
        aliases=["source"], description="Find the source of an image or linked message"
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def sauce(self, ctx, url: str | None = None):
        await ctx.defer()
        await self.replyLinks(
            ctx,
            url=url,
            saucenao=True,
            yandex=True,
            iqdb=True,
            iqdb3d=True,
            google=True,
            tineye=True,
            tracemoe=True,
            ascii2d=True,
        )

    @commands.command(aliases=["source_"])
    async def sauce_(self, ctx):
        await self.replyLinks(
            ctx,
            saucenao=True,
            yandex=True,
            iqdb=True,
            iqdb3d=True,
            google=True,
            tineye=True,
            tracemoe=True,
            ascii2d=True,
            no_preview=True,
        )

    @commands.command(aliases=["nao"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def saucenao(self, ctx):
        await self.replyLinks(ctx, saucenao=True)

    @commands.command(aliases=["nao_"])
    async def saucenao_(self, ctx):
        await self.replyLinks(ctx, saucenao=True, no_preview=True)

    @commands.command(aliases=["yan", "dex"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def yandex(self, ctx):
        await self.replyLinks(ctx, yandex=True)

    @commands.command(aliases=["yan_", "dex_"])
    async def yandex_(self, ctx):
        await self.replyLinks(ctx, yandex=True, no_preview=True)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def iqdb(self, ctx):
        await self.replyLinks(ctx, iqdb=True)

    @commands.command()
    async def iqdb_(self, ctx):
        await self.replyLinks(ctx, iqdb=True, no_preview=True)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def iqdb3d(self, ctx):
        await self.replyLinks(ctx, iqdb3d=True)

    @commands.command()
    async def iqdb3d_(self, ctx):
        await self.replyLinks(ctx, iqdb3d=True, no_preview=True)

    @commands.command(aliases=["tin", "eye"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def tineye(self, ctx):
        await self.replyLinks(ctx, tineye=True)

    @commands.command(aliases=["tin_", "eye_"])
    async def tineye_(self, ctx):
        await self.replyLinks(ctx, tineye=True, no_preview=True)

    @commands.command(aliases=["gg"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def google(self, ctx):
        await self.replyLinks(ctx, google=True)

    @commands.command(aliases=["gg_"])
    async def google_(self, ctx):
        await self.replyLinks(ctx, google=True, no_preview=True)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def tracemoe(self, ctx):
        await self.replyLinks(ctx, tracemoe=True)

    @commands.command()
    async def tracemoe_(self, ctx):
        await self.replyLinks(ctx, tracemoe=True, no_preview=True)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def ascii2d(self, ctx):
        await self.replyLinks(ctx, ascii2d=True)

    @commands.command()
    async def ascii2d_(self, ctx):
        await self.replyLinks(ctx, ascii2d=True, no_preview=True)

    async def replyLinks(
        self,
        ctx,
        url=None,
        saucenao=False,
        yandex=False,
        iqdb=False,
        iqdb3d=False,
        google=False,
        tineye=False,
        tracemoe=False,
        ascii2d=False,
        no_preview=False,
    ):
        msg = await ctx.send("Searching...")
        result = (
            ("discord link" if "/channels/" in url else "link")
            if url
            else ("history" if ctx.interaction else self.analyzeCommand(ctx))
        )

        urls = []
        if result == "file":
            urls = self.getMessageAttachmentURLs(ctx.message)

        elif result == "link":
            link = (
                url
                or ctx.message.content.replace(
                    (ctx.prefix or "") + (ctx.invoked_with or ""), ""
                ).strip()
            )
            urls = [link]

        elif result == "discord link":
            ids = re.findall(r"\d+", url or ctx.message.content, re.IGNORECASE)

            linked_guild = self.client.get_guild(int(ids[0]))
            linked_channel = linked_guild.get_channel(int(ids[1]))
            linked_message = await linked_channel.fetch_message(int(ids[2]))

            urls = self.getMessageAttachmentURLs(linked_message)

            if len(urls) == 0:
                await msg.edit(
                    content="Linked message does not have attached pictures."
                )
                return

        elif result == "history":
            async for message in ctx.channel.history(limit=50):
                if message.attachments != [] or message.embeds != []:
                    urls = self.getMessageAttachmentURLs(message)
                    break
                elif "http" in message.content:
                    for content in message.content.split():
                        if (
                            content.startswith("http")
                            and "://" in content
                            and "." in content
                            and content not in urls
                        ) and await asyncio.to_thread(self.is_url_image, content):
                            urls.append(content)
                    break
        if urls == []:
            await msg.edit(
                content=f"You have not provided anything to perform reverse search on.\nSyntax: `{self.client.command_prefix}sauce <url(image/message)/attachments>`"
            )
            return
        index = 1
        len_url = len(urls)
        if len_url > 1:
            await msg.edit(content=f"Found {len_url} images. Sending results...")
        for u in urls:
            embed = discord.Embed(colour=settings.EMBED_COLOR)
            embed.set_thumbnail(url=u)

            if result == "file":
                embed.title = f":mag_right: Results of attached files ({index})"

            elif result == "link":
                embed.title = ":mag_right: Results of provided link"

            if result == "discord link":
                embed.title = (
                    f":mag_right: Results of image attached to linked message ({index})"
                )

            if result == "history":
                embed.title = f":mag_right: Results from newest message has image in 50 newest messages ({index})"

            try:
                embed = await self.set_fields(
                    embed,
                    u,
                    saucenao,
                    yandex,
                    iqdb,
                    iqdb3d,
                    google,
                    tineye,
                    tracemoe,
                    ascii2d,
                    no_preview,
                )
                if len(urls) == 1:
                    await msg.edit(embed=embed, content=None)
                else:
                    await ctx.send(embed=embed)
            except (discord.HTTPException, ValueError, TypeError, AttributeError) as e:
                if len(urls) > 1:
                    len_url = len_url - 1
                    await msg.edit(
                        content=f"Found {len_url} images in linked message. Sending results..."
                    )
                    await ctx.send(str(e))
                else:
                    await msg.edit(content=str(e))
                    return
            del embed
            index += 1
        if len(urls) > 1:
            await msg.edit(content=f"Found {len(urls)} images.")
        return

    def analyzeCommand(self, ctx: commands.Context):
        if ((ctx.prefix or "") + (ctx.invoked_with or "")) == ctx.message.content:
            if len(ctx.message.attachments) > 0:
                return "file"
            else:
                return "history"
        else:
            if (
                re.search(
                    r"https://(ptb\.|canary\.){0,1}discord(app){0,1}\.com/channels/\d+/\d+/\d+",
                    ctx.message.content,
                    re.IGNORECASE,
                )
                != None
            ):
                return "discord link"
            else:
                return "link"

    def getMessageAttachmentURLs(self, message: discord.Message):
        urls = []

        def add_items(item: str):
            if item not in urls:
                urls.append(item)

        if "http" in message.content:
            for content in message.content.split():
                if (
                    content.startswith("http")
                    and "://" in content
                    and "." in content
                    and self.is_url_image(content)
                ):
                    add_items(content)
        if message.attachments != []:
            for a in message.attachments:
                add_items(a.url)
        if message.embeds != []:
            for embed in message.embeds:
                if embed.image.url:
                    add_items(embed.image.url)
                if embed.thumbnail.url:
                    add_items(embed.thumbnail.url)
                if embed.author.icon_url:
                    add_items(embed.author.icon_url)
                if embed.footer.icon_url:
                    add_items(embed.footer.icon_url)
        return urls

    def is_url_image(self, url: str):
        image_formats = ["image/png", "image/jpeg", "image/jpg", "image/gif"]
        r = requests.get(url, timeout=10.0)
        return r.headers["content-type"] in image_formats

    def sauceLink(self, url: str, no_preview=False):
        url_ = f"https://saucenao.com/search.php?url={parse.quote_plus(url)}"
        url_ = url_.removesuffix("%0A")
        if no_preview == True:
            return "saucenao", f"[All Results]({url_})"
        fr = self.sauce_first_result(url_)
        return "saucenao", f"[All Results]({url_})\n{fr}"

    def yandexLink(self, url: str, no_preview=False):
        url_ = f"https://yandex.com/images/search?url={parse.quote_plus(url)}&rpt=imageview"
        if url_.endswith("%0A&rpt=imageview"):
            url_ = url_.replace("%0A&rpt=imageview", "&rpt=imageview")
        if no_preview == True:
            return "yandex", f"[All Results]({url_})"
        fr = self.yandex_first_result(url_)
        return "yandex", f"[All Results]({url_})\n{fr}"

    def iqdbLink(self, url: str, no_preview=False):
        url_ = f"https://iqdb.org/?url={parse.quote_plus(url)}"
        url_ = url_.removesuffix("%0A")
        if no_preview == True:
            return "iqdb", f"[All Results]({url_})"
        fr = self.iqdb_first_result(url)
        return "iqdb", f"[All Results]({url_})\n{fr}"

    def iqdb3dLink(self, url: str, no_preview=False):
        url_ = f"https://3d.iqdb.org/?url={parse.quote_plus(url)}"
        url_ = url_.removesuffix("%0A")
        if no_preview == True:
            return "iqdb3d", f"[All Results]({url_})"
        fr = self.iqdb3d_first_result(url)
        return "iqdb3d", f"[All Results]({url_})\n{fr}"

    def tineyeLink(self, url: str, no_preview=False):
        url_ = f"https://www.tineye.com/search?url={parse.quote_plus(url)}"
        # fr = self.tineye_first_result(url_)
        if no_preview == True:
            return "tineye", f"[All Results]({url_})"
        return "tineye", f"[All Results]({url_})\n(╯‵□′)╯︵┻━┻"

    def googleLink(self, url: str, no_preview=False):
        url_ = (
            f"https://www.google.com/searchbyimage?&image_url={parse.quote_plus(url)}"
        )
        if no_preview == True:
            return "google", f"[All Results]({url_})"
        fr = self.google_first_result(url_)
        return "google", f"[All Results]({url_})\n{fr}"

    def tracemoeLink(self, url: str, no_preview=False):
        url_ = f"https://trace.moe/?auto&amp;url={parse.quote_plus(url)}"
        if no_preview == True:
            return "tracemoe", f"[All Results]({url_})"
        return "tracemoe", f"[All Results]({url_})\n(╯‵□′)╯︵┻━┻"

    def ascii2dLink(self, url: str, no_preview=False):
        url_ = f"https://ascii2d.net/search/url/{parse.quote_plus(url)}"
        if no_preview == True:
            return "ascii2d", f"[All Results]({url_})"
        return "ascii2d", f"[All Results]({url_})\n(╯‵□′)╯︵┻━┻"

    def sauce_first_result(self, url: str):
        def get_basic_html():
            try:
                html = requests.get(url, timeout=10.0).text
            except PREVIEW_ERRORS:
                html = None
            return html

        proxies, total = self.get_proxies()
        html = None
        try:
            for i in range(total - 1):
                proxy = next(proxies)
                try:
                    html = requests.get(
                        url, timeout=3.0, proxies={"http": proxy, "https": proxy}
                    ).text
                    rate_ = BeautifulSoup(html, "html.parser").find_all(
                        "div", {"class": "resultsimilarityinfo"}
                    )
                    if rate_ == []:
                        continue
                    break
                except PREVIEW_ERRORS:
                    logging.getLogger(__name__).debug(
                        "Image search preview unavailable", exc_info=True
                    )
        except PREVIEW_ERRORS:
            html = get_basic_html()
        if html is None:
            html = get_basic_html()
            if html is None:
                return "Can't get first result."
        rate_ = BeautifulSoup(html, "html.parser").find_all(
            "div", {"class": "resultsimilarityinfo"}
        )
        if rate_ == []:
            return "Reaching rate limit. Please click the above url to view results."
        rate = rate_[0].get_text()[:-1]
        if float(rate) < 50.00:
            return "Low similarity results."
        re = BeautifulSoup(html, "html.parser").find_all(
            "div", {"class": "resultcontent"}
        )[0]
        title = BeautifulSoup(
            str(
                BeautifulSoup(str(re), "html.parser").find_all(
                    "div", {"class": "resulttitle"}
                )[0]
            ),
            "html.parser",
        ).get_text()
        columms = BeautifulSoup(str(re), "html.parser").find_all(
            "div", {"class": "resultcontentcolumn"}
        )
        strong, urls, url_vals = [], [], []
        columm = BeautifulSoup(str(columms[0]), "html.parser")
        for strong_ in columm.find_all("strong"):
            strong.append(strong_.get_text())
        for link in columm.find_all("a"):
            href = link.get("href")
            if isinstance(href, str):
                urls.append(href)
                url_vals.append(link.get_text())
        if urls == []:
            misc = BeautifulSoup(html, "html.parser").find_all(
                "div", {"class": "resultmiscinfo"}
            )[0]
            url_ = BeautifulSoup(str(misc), "html.parser").find("a")
            try:
                if not isinstance(url_, Tag):
                    return f"__First Result__\n{title}"
                href = url_.get("href")
                if not isinstance(href, str):
                    return f"__First Result__\n{title}"
                return f"__First Result__\n[{title}]({href})"
            except PREVIEW_ERRORS:
                return f"__First Result__\n{title}"
        for count, val in enumerate(urls):
            if "saucenao.com" in val:
                pass
            else:
                return f"__First Result__\n{title}\n{strong[count]}[{url_vals[count]}]({val})"

    def yandex_first_result(self, url: str):
        html = None
        scraper = cloudscraper.create_scraper(delay=10)

        def get_basic_html():
            try:
                html = scraper.get(url, timeout=10.0).text
            except PREVIEW_ERRORS:
                html = None
            return html

        proxies, total = self.get_proxies()
        html = None
        try:
            for i in range(total - 1):
                proxy = next(proxies)
                try:
                    html = scraper.get(
                        url, timeout=2.0, proxies={"http": proxy, "https": proxy}
                    ).text
                    emty = BeautifulSoup(html, "html.parser").find_all(
                        "div", {"class": "CbirOtherSizes-EmptyMessage"}
                    )
                    if emty != []:
                        return "No matching images found."
                        break
                except PREVIEW_ERRORS:
                    logging.getLogger(__name__).debug(
                        "Image search preview unavailable", exc_info=True
                    )
        except PREVIEW_ERRORS:
            html = get_basic_html()
        if html is None:
            html = get_basic_html()
            if html is None:
                return "Can't get first result."
        emty = BeautifulSoup(html, "html.parser").find_all(
            "div", {"class": "CbirOtherSizes-EmptyMessage"}
        )
        if emty != []:
            return "No matching images found."
        item = BeautifulSoup(html, "html.parser").find(
            "a",
            {
                "class": "link link_theme_normal other-sites__snippet-title-link i-bem link_js_inited"
            },
        )
        if item is None:
            item = BeautifulSoup(html, "html.parser").find(
                "a",
                {
                    "class": "link link_theme_normal other-sites__snippet-title-link i-bem"
                },
            )
            if item is None:
                item = BeautifulSoup(html, "html.parser").find(
                    "a",
                    {
                        "class": "link link_theme_outer other-sites__snippet-site-link i-bem link_js_inited"
                    },
                )
                if item is None:
                    item = BeautifulSoup(html, "html.parser").find(
                        "a",
                        {
                            "class": "link link_theme_outer other-sites__snippet-site-link i-bem"
                        },
                    )
                    if item is None:
                        item = BeautifulSoup(html, "html.parser").find(
                            "a", {"class": "Link Link_theme_normal"}
                        )
        if not isinstance(item, Tag):
            return "Can't get first result."
        try:
            url_ = item.get("href")
            text = item.get_text()
            if url_ is None or text is None:
                return "Can't get first result."
            return f"__First Result__\n[{text}]({url_})"
        except PREVIEW_ERRORS:
            return "Can't get first result."

    def iqdb_first_result(self, url: str):
        try:
            data = {"url": url}
            html = requests.post("https://www.iqdb.org", data=data, timeout=10.0).text
        except PREVIEW_ERRORS:
            return "Can't get first result."
        nomatch = BeautifulSoup(html, "html.parser").find_all(
            "div", {"class": "nomatch"}
        )
        if nomatch != []:
            return "No relevant matches."
        pages = BeautifulSoup(html, "html.parser").find_all(
            "div", {"class": "pages", "id": "pages"}
        )
        if pages == []:
            return "File to large."
        bm = BeautifulSoup(str(pages), "html.parser").find_all("td", {"class": "image"})
        try:
            anchor = BeautifulSoup(str(bm[1]), "html.parser").find("a")
            if not isinstance(anchor, Tag):
                return "Can't get first result."
            url_ = anchor.get("href")
            if not isinstance(url_, str):
                return "Can't get first result."
            url_ = parse.urljoin("https://iqdb.org/", url_)
            text = parse.urlsplit(url_).netloc
            if url_ is None or text is None:
                return "Can't get first result."
            return f"__Best match__\n[{text}]({url_})"
        except PREVIEW_ERRORS:
            return "Can't get first result."

    def iqdb3d_first_result(self, url: str):
        try:
            data = {"url": url}
            html = requests.post("https://3d.iqdb.org", data=data, timeout=10.0).text
        except PREVIEW_ERRORS:
            return "Can't get first result."
        nomatch = BeautifulSoup(html, "html.parser").find_all(
            "div", {"class": "nomatch"}
        )
        if nomatch != []:
            return "No relevant matches."
        pages = BeautifulSoup(html, "html.parser").find_all(
            "div", {"class": "pages", "id": "pages"}
        )
        if pages == []:
            return "File to large."
        bm = BeautifulSoup(str(pages), "html.parser").find_all("td", {"class": "image"})
        try:
            anchor = BeautifulSoup(str(bm[1]), "html.parser").find("a")
            if not isinstance(anchor, Tag):
                return "Can't get first result."
            url_ = anchor.get("href")
            if not isinstance(url_, str):
                return "Can't get first result."
            url_ = parse.urljoin("https://iqdb.org/", url_)
            text = parse.urlsplit(url_).netloc
            if url_ is None or text is None:
                return "Can't get first result."
            return f"<u>First Result</u><br><a href='{url_}' target='_blank' rel='noopener noreferrer'>{text}</a>"
        except PREVIEW_ERRORS:
            return "Can't get first result."

    def tineye_first_result(self, url: str):
        # the site need to render javascript but also having bot protection
        # javascript render can use requests_html
        # cloudscraper can deal with bot protection
        # but can't use 2 of above libs at the same time / need to use selenium or another lightweight solution
        try:
            scraper = cloudscraper.create_scraper()
            html = scraper.get(url).text
        except PREVIEW_ERRORS:
            return "Can't get first result."
        match_ = BeautifulSoup(html, "html.parser").find(
            "div", {"class": "matches col-sm-12"}
        )
        match = BeautifulSoup(str(match_), "html.parser").find("h4")
        if not isinstance(match, Tag):
            return "Can't get first result."
        try:
            text = match.get("title")
            anchor = BeautifulSoup(str(match), "html.parser").find("a")
            if not isinstance(anchor, Tag):
                return "Can't get first result."
            url_ = anchor.get("href")
            if text is None or url_ is None:
                return "Can't get first result."
            return f"__First Result__\n[{text}]({url_})"
        except PREVIEW_ERRORS:
            return "Can't get first result."

    def google_first_result(self, url: str):
        scraper = cloudscraper.create_scraper(delay=10)
        html = None
        try:
            re = requests.get(url, timeout=15.0)
            for resp in re.history:
                if "search?" in resp.url:
                    html = scraper.get(url, timeout=15.0).text
                    break
            if html is None:
                return "Can't get first result."
        except PREVIEW_ERRORS:
            return "Can't get first result."
        sizes = BeautifulSoup(html, "html.parser").find_all("div", {"class": "O1id0e"})
        all_sizes = BeautifulSoup(str(sizes), "html.parser").find_all(
            "span", {"class": "gl"}
        )
        if all_sizes == []:
            return "No other sizes of this image found."
        try:
            anchor = BeautifulSoup(str(all_sizes[0]), "html.parser").find("a")
            if not isinstance(anchor, Tag):
                return "Can't get first result."
            href = anchor.get("href")
            if not isinstance(href, str):
                return "Can't get first result."
            all_sizes_url = parse.urljoin("https://www.google.com/", href)
            time.sleep(1)
            html = scraper.get(all_sizes_url).text
        except PREVIEW_ERRORS:
            return "Can't get first result."
        imgs = BeautifulSoup(html, "html.parser").find_all("div", {"jsname": "N9Xkfe"})
        try:
            first = BeautifulSoup(str(imgs[0]), "html.parser").find_all("a")
            url_ = first[1].get("href")
            text = first[1].get("title")
            if url_ is None or text is None:
                return "Can't get first result."
            return f"__First Result__\n[{text}]({url_})"
        except PREVIEW_ERRORS:
            return "Can't get first result."

    async def set_fields(
        self,
        embed,
        u,
        saucenao=False,
        yandex=False,
        iqdb=False,
        iqdb3d=False,
        google=False,
        tineye=False,
        tracemoe=False,
        ascii2d=False,
        no_preview=False,
    ):
        enabled = [saucenao, yandex, iqdb, iqdb3d, google, tineye, tracemoe, ascii2d]
        engines = [
            self.sauceLink,
            self.yandexLink,
            self.iqdbLink,
            self.iqdb3dLink,
            self.googleLink,
            self.tineyeLink,
            self.tracemoeLink,
            self.ascii2dLink,
        ]
        results = await asyncio.gather(
            *(
                asyncio.to_thread(engine, u, no_preview)
                for engine, active in zip(engines, enabled)
                if active
            ),
            return_exceptions=True,
        )
        names = {
            "saucenao": "SauceNAO",
            "yandex": "Yandex",
            "iqdb": "IQDB",
            "iqdb3d": "IQDB3D",
            "google": "Google",
            "tineye": "TinEye",
            "tracemoe": "TraceMoe",
            "ascii2d": "ASCII2D",
        }
        for result in results:
            if isinstance(result, BaseException):
                continue
            name, text = result
            embed.add_field(name=names.get(name, name), value=str(text)[:1024])
        return embed

    def get_proxies(self):
        url = "https://free-proxy-list.net/"
        response = requests.get(url, timeout=10)
        parser = fromstring(response.text)
        proxies = set()
        proxies_yes = []
        proxies_no = []
        total = 0
        for i in parser.xpath("//tbody/tr")[:10]:
            proxy = ":".join(
                [i.xpath(".//td[1]/text()")[0], i.xpath(".//td[2]/text()")[0]]
            )
            if i.xpath('.//td[7][contains(text(),"yes")]'):
                proxies_yes.append(proxy)
            elif i.xpath('.//td[7][contains(text(),"no")]'):
                proxies_no.append(proxy)
            total += 1
        for proxy in proxies_yes:
            proxies.add(proxy)
        for proxy in proxies_no:
            proxies.add(proxy)
        return cycle(proxies), total


async def setup(client):
    await client.add_cog(Sauce(client))
