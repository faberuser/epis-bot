# epis-bot

A Discord Bot made for King's Raid mobile game

Game data in `kingsraid-data/` is supplied by a Git submodule, with legacy as the default and optional versions per command. Initialize it with `git submodule update --init --recursive`.

## You can get

- Heroes's information, skills, perks, books, uws, uts, sws, splashart, visual splashart, costumes.
- Artifacts's information, Bosses's information and skills.
- New tweets from [@kingsraid_msg](https://x.com/kingsraid_msg) and official [KING's RAID RE:VERSE Steam announcements](https://store.steampowered.com/news/app/3689540).
- King's Raid Guide from KR Encyclopedia (the bot need to be in the server).
- Softcap and other things.

## Installations

### Requirements

- Python 3.12 (tested).
- Discord Bot's Token from [Discord Developers](https://discord.com/developers/applications).

### Installations

1. Create a virtual environment with `python -m venv .venv`. Activate it with `.venv\Scripts\activate` on Windows or `source .venv/bin/activate` on Linux/macOS.
2. Initialize game data with `git submodule update --init --recursive`, then install dependencies with `python -m pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and set `DISCORD_TOKEN`. On PowerShell: `Copy-Item .env.example .env`; on Linux/macOS: `cp .env.example .env`.
4. Run `python main.py`.

### Environment configuration

All settings come from environment variables. For local development, `settings.py` loads `.env` from the repository root. Variables already supplied by your shell or hosting platform take precedence. Restart the bot after changing settings. `.env` is ignored by Git; `.env.example` contains the documented template.

| Variable             | Format and default                                                                                                                                       |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `DISCORD_TOKEN`      | Required Discord bot token.                                                                                                                              |
| `PREFIX`             | JSON list of default prefixes; defaults to `["/", "."]`. In `.env`, use `PREFIX='["/", "."]'`. Per-server overrides in `data/prefixes.json` still apply. |
| `BEARER_TOKEN`       | Optional X API bearer token with user lookup and timeline access for `kingsraid_msg`. Blank disables Twitter polling. Steam needs no API key.            |
| `STEAM_PROXY_URL` | Optional HTTP proxy for Steam announcements, e.g. `http://192.168.1.9:1080`. Blank connects directly. Uses the HTTP mode of proxies that support both HTTP and SOCKS5. |
| `GITHUB_REPO` | Repository to track in `owner/repository` format, e.g. `faberuser/sprk`. Blank disables tracking. |
| `GITHUB_BRANCH` | Exact branch name, e.g. `development`. Blank disables tracking. |
| `GITHUB_TOKEN` | Optional token for public repositories; private repositories require a token with Contents read permission. |
| `KR_DEFAULT_VERSION` | Default game dataset, `legacy`. Override per command with the slash `version` option or prefix `--version <name>` or `-V <name>`.                        |
| `KR_LANGUAGE`        | Default game-data language, `en`, for users without a saved preference.                                                                                  |
| `KRE_GUILD_ID`       | Guide source server ID, as an integer. Defaults to `0` (disabled).                                                                                       |
| `KRE_CATEGORIES`     | Comma-separated category IDs, e.g. `123456789012345678,234567890123456789`. Blank disables guides.                                                       |
| `KRE_INVITE`         | Optional invite URL displayed with guides. Blank omits the attribution link.                                                                             |

Use `github on`, `github off`, and `github status` (prefix or slash commands) to manage commit announcements in each channel. Turning tracking on or off requires Manage Channels. The bot polls every five minutes, establishes a baseline on its first successful check, and then posts new commits with their author, message, and commit link. It reads the latest 100 commits per check; commits outside that window after a long outage may be missed. Delivery history and subscriptions persist under ignored `data/github/`. Changing the repository or branch creates separate subscription state; enable it again in the desired channels. No token is needed for public repositories. API errors leave delivery history unchanged and retry on the next poll.

Use `steam latest`, `twitter latest`, or `github latest` (prefix or slash) to show the newest item on demand, even without a channel subscription. These commands do not change subscription or delivery history. Each has a 30-second cooldown per user. Twitter still requires BEARER_TOKEN; GitHub requires a configured repository and branch.
