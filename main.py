from fasthtml.common import *
from markupsafe import *
import re, os, requests

# Define the bootstrap version and CDN links
# Todo REMOVE hardcoded version and use the built in pico-css and fh-bootstrap versions
cdn = 'https://cdn.jsdelivr.net/npm/bootstrap'
bootstrap_links = [
    Link(href=cdn+"@5.3.3/dist/css/bootstrap.min.css", rel="stylesheet"),
    Script(src=cdn+"@5.3.3/dist/js/bootstrap.bundle.min.js"),
    Link(href=cdn+"-icons@1.11.3/font/bootstrap-icons.min.css", rel="stylesheet")
]

## Todo Add these to the page meta
title = "Steam Headless"
meta_description = "Companion App"
meta_keywords = "web, steam, headless, sunshine, python, FastHTML"

## Define how to desiplay the games in the list
def render(game):
    return Li(
        Grid(
            Strong(
                game.game_name, 
                cls='list-group-item border-end-0 d-inline-block text-truncate',
            ),
            A(
                'Add To Sunshine', hx_get=f'/add/{game.game_id}', target_id=f'appid-{game.game_id}', 
                cls='btn btn-primary me-2'
            ),
            A(
                'Remove', hx_get=f'/remove/{game.game_id}', target_id=f'appid-{game.game_id}', 
                cls='btn btn-danger me-2'
            ),
            Strong(
                ('✅' if game.game_added else '❌'),
                id=f'appid-{game.game_id}'
            )
        )
    )

# Define the sidebar items
def SidebarItem(text, hx_get, hx_target, **kwargs):
    return Div(
        I(cls=f'bi bi-{text}'),
        Span(text),
        hx_get=hx_get, hx_target=hx_target,
        data_bs_parent='#sidebar', role='button',
        cls='list-group-item border-end-0 d-inline-block text-truncate',
        **kwargs)

# Define the sidebar
def Sidebar(sidebar_items, hx_get, hx_target):
    return Div(
        Div(*(SidebarItem(o, f"{hx_get}?menu={o}", hx_target) for o in sidebar_items),
            id='sidebar-nav',
            cls='list-group border-0 rounded-0 text-sm-start min-vh-100'
        ),
        id='sidebar',
        cls='collapse collapse-horizontal show border-end')

# Add remove buttons to the sidebar
sidebar_items = ('WebUI', 'Sunshine WebUI', 'Logs', 'Installers', 'Sunshine Manager', 'FAQ')

# Define the main fastHTML app
app,rt,gamedb,Game = fast_app('data/gamedb.db', 
    render=render,
    game_id=int, 
    game_name=str, 
    game_added=bool, 
    pk='game_id', 
    live=True, # Todo remove live for final version
    hdrs=bootstrap_links)

# The Log Page content is defined here
# Todo seperate the page into a different file
def logs_content():
    logs_dir = "/home/default/.cache/log"
    log_files = [f for f in os.listdir(logs_dir) if os.path.isfile(os.path.join(logs_dir, f)) and f.endswith('.log')]
    
    divs = []
    for log_file in log_files:
        file_path = os.path.join(logs_dir, log_file)
        with open(file_path, 'r') as file:
            lines = file.readlines()[-50:]
            content = "<br>".join(lines)
            divs.append(Details(Summary(escape(log_file), role='button'), P(Markup(content), cls='card')))

    return Div(*divs) if divs else Div("No log files found.")

# The Installer Page content is defined here
# Todo seperate the page into a different file
def installers_content():
    installer_dir = "/home/default/.cache/installers"
    installers = [f for f in os.listdir(installer_dir) if os.path.isfile(os.path.join(installer_dir, f)) and f.endswith('.sh')]

    divs = []
    for installer in installers:
        divs.append(Button(installer, onclick=f"fireScript('{installer}')", cls='btn btn-primary me-2 card container'))

    return Div(*divs) if divs else Div("No installers found.")

# Function to populate SQLite database with Steam games
def get_installed_steam_games(directory):
    games = gamedb()
    for filename in os.listdir(directory):
        if filename.endswith('.acf'):
            acf_path = os.path.join(directory, filename)
            with open(acf_path, 'r', encoding='utf-8') as acf_file:
                content = acf_file.read()
                game_id_match = re.search(r'"appid"\s*:\s*"(\d+)"', content)
                if game_id_match:
                    _game_id = game_id_match.group(1)
                    name_match = re.search(r'"name"\s*:\s*"([^"]+)"', content)
                    if name_match:
                        _game_name = name_match.group(1)
                        if _game_id in games:
                            continue
                        else:
                            gamedb.insert(Game(
                                game_id=_game_id, 
                                game_name=_game_name, 
                                game_added=false
                            ))

# The Sunshine Manager Page content is defined here
# Todo seperate the page into a different file
def sunshine_manager_content():
    _reload = Button( 
        "Reload Steam Games",
        onclick=get_installed_steam_games('/mnt/games/SteamLibrary/steamapps'),
        cls='btn btn-primary container rtl'
    )
    return Div(
        H1("Sunshine Manager"),
        cls='container'
    ), Div(
        Br(),
        _reload,
        Div (
            Ul(*gamedb()),
            cls='list-group'
        )
    )

# The Faq Page content is defined here
# Todo seperate the page into a different file
def faq_content():
    url = "https://raw.githubusercontent.com/Steam-Headless/docker-steam-headless/refs/heads/master/docs/troubleshooting.md"
    response = requests.get(url)
    if response.status_code == 200:
        _content = response.text
    else:
        _content = "Failed to load content."
    
    return Div(
        H1("FAQ"),
        P(
            _content,
            cls='container'
        )
    )

# Define the routes for the application
# The Main route when visiting the page
@rt('/')
def get():
    return Div(
        Div(
            Div(
                Sidebar(sidebar_items, hx_get='menucontent', hx_target='#current-menu-content'),
                cls='col-auto px-0'),
            Main(
                A(I(cls='bi bi-list bi-lg py-2 p-1'), 'Menu',
                  href='#', data_bs_target='#sidebar', data_bs_toggle='collapse', aria_expanded='false', aria_controls='sidebar',
                  cls='border rounded-3 p-1 text-decoration-none'),
                Div(
                  Div(
                    Div(
                    H1("Welcome to Steam Headless!"),
                    P("Select an Item to get started"),
                    id="current-menu-content", style="width: 100%; height: 100vh;"),
                    cls='col-12'
                ), cls='row'),
                cls='col ps-md-2 pt-2'),
            cls='row flex-nowrap'),
        cls='container-fluid')

# The route for the menu content, which is dynamically loaded
@rt('/menucontent')
def menucontent(menu: str):
    switch_cases = {
        'WebUI': f'<iframe src="http://192.168.100.131:8083" width="100%" height="100%" style="border:none; allow-insecure"></iframe>',
        'Sunshine WebUI': f'<iframe src="https://192.168.100.131:47990" width="100%" height="100%" style="border:none; allow-insecure"></iframe>',
        'Logs': logs_content(),
        'Installers': installers_content(),
        'Sunshine Manager': sunshine_manager_content(),
        'FAQ': faq_content()
    }

    return switch_cases.get(menu, Div("No content available"))

# The route to remove a game from sunshine
@rt('/remove/{game_id}')
def get(game_id:int):
    game = gamedb.get[game_id]
    game.game_added = False
    return gamedb.update(game)

# The route to add a game to sunshine
@rt('/add/{game_id}')
def get(game_id:int):
    game = gamedb.get[game_id]
    game.game_added = True
    return gamedb.update(game)

# Serve the application at port 8082
serve(port=8082)
