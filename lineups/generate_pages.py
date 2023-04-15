import requests
import re
import textwrap
import os
import itertools
from pathlib import Path
from yattag import Doc, indent

def main():

    TOKEN = os.environ['NOTION']

    agents = {
        'astra',
        'brimstone',
        'harbor',
        'omen',
        'viper',

        'jett',
        'neon',
        'phoenix',
        'raze',
        'reyna',
        'yoru',

        'breach',
        'fade',
        'gekko',
        'kayo',
        'skye',
        'sova',

        'chamber',
        'cypher',
        'killjoy',
        'sage',
    }

    maps = {
        'bind': {'a', 'b'},
        'haven': {'a', 'b', 'c'},
        'split': {'a', 'b'},
        'ascent': {'a', 'b'},
        'icebox': {'a', 'b'},
        'breeze': {'a', 'b'},
        'fracture': {'a', 'b'},
        'pearl': {'a', 'b'},
        'lotus': {'a', 'b', 'c'}
    }

    sides = {'attacker', 'defender'}

    counter = 1
    count_full = len(sides) * len(list(itertools.chain.from_iterable(list(maps.values())))) * len(agents)
    for val_side in sides:
        for val_map, val_site_set in maps.items():
            for val_site in val_site_set:
                for val_agent in agents:
                    final_directory = Path('content', val_side, val_map, val_site, val_agent)
                    if not final_directory.is_dir():
                        print(f'{counter}/{count_full} Creating {final_directory}')
                        final_directory.mkdir(parents=True, exist_ok=True)
                    else:
                        print(f'{counter}/{count_full} Found {final_directory}')
                    counter += 1

    def normalize_agent_name(name):
        normalized = {
            'KAY/O': 'kayo'
        }
        return (normalized.get(name, name)).casefold()

    def get_valid_filename(name):
        """
        Return the given string converted to a string that can be used for a clean
        filename. Remove leading and trailing spaces; convert other spaces to
        underscores; and remove anything that is not an alphanumeric, dash,
        underscore, or dot.
        >>> get_valid_filename("john's portrait in 2004.jpg")
        'johns_portrait_in_2004.jpg'
        """
        s = str(name).strip().replace(" ", "_")
        s = re.sub(r"(?u)[^-\w.]", "", s)
        if s in {"", ".", ".."}:
            raise RuntimeError("Could not derive file name from '%s'" % name)
        return s

    query_url = 'https://api.notion.com/v1/databases/ad0cbfb7d1a24784a1b4d8f14eb8fc28/query'
    headers = {
        'Authorization': 'Bearer ' + TOKEN,
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    generated_paths = []
    database = requests.post(query_url, headers=headers).json()['results']
    for page in database:
        props = page['properties']
        page_name = str(props['Name']['title'][0]['text']['content'])
        page_site = str(props['Site']['select']['name']).casefold()
        page_map = str(props['Map']['select']['name']).casefold()
        page_agents = [normalize_agent_name(agent['name']) for agent in props['Agent']['multi_select']]
        page_side = str(props['Side']['select']['name']).casefold()

        page_path = Path('content', page_side, page_map, page_site, page_agents[0], get_valid_filename(page_name)).with_suffix('.html')
        html_page = textwrap.dedent(f'''<!DOCTYPE html>
        <html>
            <head>
                <meta charset="UTF-8">
                <meta http-equiv="X-UA-Compatible" content="IE=edge">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta http-equiv="refresh" content="0; url='https://gatecrash.notion.site/{page["id"]}'" />
                <title>{page_name}</title>
            </head>
            <body>
                <p><a href="https://gatecrash.notion.site/{page["id"]}">Redirect</a></p>
            </body>
        </html>
                        ''')
        with page_path.open('w', encoding='UTF-8') as file:
            file.write(html_page)
        generated_paths.append(page_path.as_posix())
        print('Finished:', page_path)

    with Path('index.html').open('w', encoding='UTF-8') as file:
        doc, tag, text = Doc().tagtext()

        doc.asis('<!DOCTYPE html>')
        with tag('html'):
            with tag('head'):
                doc.stag('meta', charset='UTF-8')
                doc.stag('meta', name='viewport', content='width=device-width, initial-scale=1')
                doc.stag('meta', name='description', content='')
            with tag('body'):
                with tag('p'):
                    text('Welcome to the VALORANT Lineups and Setups redirect page. This website just used for development, so don\'t expect anything with effort.')
                with tag('p'):
                    with tag('a', href='https://gatecrash.notion.site/VALORANT-Lineups-and-Setups-233eac1e8a7d4a21bb9f49e59054fb04'):
                        text('VALORANT Lineups and Setups')
                with tag('ul'):
                    for url_path in generated_paths:
                        with tag('li'):
                            with tag('a', href=f'/lineups/{url_path}'):
                                text(str(url_path))

        file.write(indent(doc.getvalue()))
