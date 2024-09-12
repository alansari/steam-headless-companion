from fasthtml.common import *
import os
import time

cdn = 'https://cdn.jsdelivr.net/npm/bootstrap'
bootstrap_links = [
    Link(href=cdn+"@5.3.3/dist/css/bootstrap.min.css", rel="stylesheet"),
    Script(src=cdn+"@5.3.3/dist/js/bootstrap.bundle.min.js"),
    Link(href=cdn+"-icons@1.11.3/font/bootstrap-icons.min.css", rel="stylesheet")
]

app,rt = fast_app(live=True,hdrs=bootstrap_links)

def get_current_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def meta():
    title = "Steam Headless"
    meta_description = "Companion App"
    meta_keywords = "web, steam, headless, sunshine, python, FastHTML"
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <meta name="description" content="{meta_description}">
        <meta name="keywords" content="{meta_keywords}">
    </head>
    """
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

sidebar_items = ('WebUI', 'Sunshine WebUI', 'Services', 'Installers', 'Sunshine Manager', 'FAQ')

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

@rt('/menucontent')
def menucontent(menu: str):
    switch_cases = {
        'WebUI': f'<iframe src="http://192.168.100.131:8083" width="100%" height="100%" style="border:none;" allow-insecure></iframe>',
        'Sunshine WebUI': f'<iframe src="https://192.168.100.131:47990" width="100%" height="100%" style="border:none;"></iframe>',
        'Services': Div("Content for Services"),
        'Installers': Div("Content for Installers"),
        'Sunshine Manager': Div("Content for Sunshine Manager"),
        'FAQ': Div("Content for FAQ")
    }
    
    return switch_cases.get(menu, Div("No content available"))

serve(port=8082)