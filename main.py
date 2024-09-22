from fasthtml.common import *
from markupsafe import *
import re
import os

cdn = 'https://cdn.jsdelivr.net/npm/bootstrap'
bootstrap_links = [
    Link(href=cdn+"@5.3.3/dist/css/bootstrap.min.css", rel="stylesheet"),
    Script(src=cdn+"@5.3.3/dist/js/bootstrap.bundle.min.js"),
    Link(href=cdn+"-icons@1.11.3/font/bootstrap-icons.min.css", rel="stylesheet")
]
title = "Steam Headless"
meta_description = "Companion App"
meta_keywords = "web, steam, headless, sunshine, python, FastHTML"

# How to render elements from sqlite database
def render(Game):
    games = Game.select()
    rows = []
    for game in games:
        row = Div(
            H3(game.game_name),
            P('Added: ' + str(game.game_added)),
            A('Delete', href=f'/delete/{game.game_id}', classes='btn btn-error')
        )
        rows.append(row)
    return Div(*rows, classes='grid grid-cols-1 gap-4')

# Define the FastHTML app with database initialization/load, routing, rendering, ***and builtin pico/bootstrap CSS theme hdrs=pico-links
app,rt,gamedb,games = fast_app('data/gamedb.db', 
    game_id=int, 
    game_name=str, 
    game_added=bool, pk='game_id', 
    live=True, 
    render=render,
    hdrs=bootstrap_links
)

def SidebarItem(text, hx_get, hx_target, **kwargs):
    return Div(
        I(cls=f'bi bi-{text}'),
        Span(text),
        hx_get=hx_get, hx_target=hx_target,
        data_bs_parent='#sidebar', role='button',
        cls='list-group-item border-end-0 d-inline-block text-truncate',
        **kwargs)

def Sidebar(sidebar_items, hx_get, hx_target):
    return Div(
        Div(*(SidebarItem(o, f"{hx_get}?menu={o}", hx_target) for o in sidebar_items),
            id='sidebar-nav',
            cls='list-group border-0 rounded-0 text-sm-start min-vh-100'
        ),
        id='sidebar',
        cls='collapse collapse-horizontal show border-end')

sidebar_items = ('WebUI', 'Sunshine WebUI', 'Logs', 'Installers', 'Sunshine Manager', 'FAQ')

# This whole section to be replaced by layout() function in the future.
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

def installers_content():
    installer_dir = "/home/default/.cache/installers"
    installers = [f for f in os.listdir(installer_dir) if os.path.isfile(os.path.join(installer_dir, f)) and f.endswith('.sh')]

    divs = []
    for installer in installers:
        divs.append(Button(installer, onclick=f"fireScript('{installer}')", cls='btn btn-primary me-2 card container'))

    return Div(*divs) if divs else Div("No installers found.")

def get_installed_steam_games(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.acf'):
            acf_path = os.path.join(directory, filename)
            with open(acf_path, 'r', encoding='utf-8') as acf_file:
                content = acf_file.read()
                game_id_match = re.search(r'"appid"\s*:\s*"(\d+)"', content)
                if game_id_match:
                    game_id = game_id_match.group(1)
                    name_match = re.search(r'"name"\s*:\s*"([^"]+)"', content)
                    if name_match:
                        game_name = name_match.group(1)
                        if game_id in games:
                            continue
                        else:
                            games.insert(game_id, game_name, false)

# Define the HTML layout using fasthtml built-in pico-css and bootstrap test
def layout():
    return Body(
        Header('Steam-Headless', 
            dir='rtl',
            cls='container-fluid', 
            style="border-style: dotted; border-color: white"
        ),
        Main(
            Button(
                    "Menu",
                    cls='aria-controls=sidebar, aria-expanded=false',
                    onlclick='aria-controls="sidebar" aria-expanded="true"',
                ),
            Aside(
                Nav(
                    Ul(Li(*[A(item, href=f'/{re.sub(" ", "-", item)}') for item in sidebar_items])),
                    cls='nav flex-column'
                ),
                cls='sidebar aria-label=sidebar position-fixed top-0 start-0 vh-100 bg-light shadow'
            ),
            Div(
                H1('Hello'),
                cls='',
                style='background-color: blue'
            ),
            cls='container-fluid',
            style="border-style: dotted; border-color: white"
        ),
        Footer('Footer',
            cls='container-fluid',
            style="border-style: dotted; border-color: white"
        ),
        cls='container-fluid'
    )

def sunshine_manager_content():
    #get_installed_steam_games("/mnt/games/SteamLibrary/steamapps")
    return Div(
        H1("Sunshine Manager"),
        Button("Start Sunshine", onclick="startSunshine()", cls='btn btn-primary me-2'),
        Button("Stop Sunshine", onclick="stopSunshine()", cls='btn btn-danger me-2'),
        cls='container'
    )

def faq_content():
    return Div(
        H1("FAQ"),
        P("Here you can find answers to frequently asked questions."),
        cls='container'
    )

@rt('/menucontent')
def menucontent(menu: str):
    switch_cases = {
        'WebUI': f'<iframe src="http://192.168.100.131:8083" width="100%" height="100%" style="border:none;"></iframe>',
        'Sunshine WebUI': f'<iframe src="https://192.168.100.131:47990" width="100%" height="100%" style="border:none; allow-insecure"></iframe>',
        'Logs': logs_content(),
        'Installers': installers_content(),
        'Sunshine Manager': sunshine_manager_content(),
        'FAQ': faq_content()
    }

    return switch_cases.get(menu, Div("No content available"))

serve(port=8082)
