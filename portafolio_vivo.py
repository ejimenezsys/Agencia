"""Módulo de Portafolio en Vivo (/portafolio-vivo/{slug}).

Expone los sitios web reales desarrollados en el workspace local para que los closers
y visitantes de /paginas-web puedan recorrerlos en vivo, con degradación elegante si algún
directorio hermano no está presente en despliegues en contenedor.
"""
import os
import re
from typing import Dict, Optional
from fastapi import APIRouter, FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

router = APIRouter()

AGENCIA_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_SITES_DIR = os.path.abspath(os.path.join(AGENCIA_DIR, ".."))


def _resolve_site_dir(*parts: str) -> Optional[str]:
    """Busca primero dentro de agencia/portafolio_vivo y luego en el directorio padre."""
    candidate_local = os.path.join(AGENCIA_DIR, "portafolio_vivo", *parts)
    if os.path.isdir(candidate_local):
        return candidate_local
    candidate_parent = os.path.join(PARENT_SITES_DIR, *parts)
    if os.path.isdir(candidate_parent):
        return candidate_parent
    return None


STATIC_PORTFOLIO_MAP: Dict[str, Dict[str, Optional[str]]] = {
    "servixo": {
        "dir": _resolve_site_dir("BIB-home-services-box-user", "mi-negocio", "website"),
        "fallback_url": "/demo-sitio-web?template=servicios_locales_taller",
    },
    "doralbusinesscity": {
        "dir": _resolve_site_dir("doralbusinesscity"),
        "fallback_url": "https://doralbusinesscity.com/",
    },
    "idoljoseofficial": {
        "dir": _resolve_site_dir("idoljoseofficial"),
        "fallback_url": "https://idoljoseofficial.com/",
    },
    "idoljosegroupcorp": {
        "dir": _resolve_site_dir("idoljosegroupcorp"),
        "fallback_url": "https://idoljosegroupcorp.com/",
    },
    "suesenciaastral": {
        "dir": _resolve_site_dir("suesenciaastral", "dist") or _resolve_site_dir("suesenciaastral"),
        "fallback_url": "https://generatucartaastral.com/",
    },
    "edwardjimenezia": {
        "dir": _resolve_site_dir("edwardjimenezia"),
        "fallback_url": "https://edwardjimenezia.com/",
    },
    "edwardjimenez": {
        "dir": _resolve_site_dir("edwardjimenez"),
        "fallback_url": "https://edwardjimenez.com/",
    },
}

BLANCOS_DIST_DIR = _resolve_site_dir("blancosgirasol", "proyecto-blancos-girasol", "dist")
JPX_DIR = _resolve_site_dir("jpxinternational")
SUNOTARIA_DIR = _resolve_site_dir("sunotariausa")
SYNETCOM_DIR = _resolve_site_dir("synetcom", "synetcom")


def _inject_base_href(html_text: str, base_href: str) -> str:
    """Inserta <base href=...> justo después de <head> para resolver rutas relativas."""
    if "<base " in html_text.lower():
        return html_text
    return re.sub(
        r"(<head[^>]*>)",
        rf'\1\n  <base href="{base_href}">',
        html_text,
        count=1,
        flags=re.IGNORECASE,
    )


def _serve_static_site_file(base_dir: str, prefix: str, subpath: str = ""):
    """Sirve index.html o un archivo estático seguro dentro de base_dir."""
    clean_sub = (subpath or "").lstrip("/")
    if not clean_sub:
        clean_sub = "index.html"
    safe_target = os.path.abspath(os.path.join(base_dir, clean_sub))
    base_abs = os.path.abspath(base_dir)
    if not safe_target.startswith(base_abs):
        raise HTTPException(status_code=403, detail="Ruta no permitida.")
    if os.path.isdir(safe_target):
        safe_target = os.path.join(safe_target, "index.html")
    if not os.path.exists(safe_target):
        raise HTTPException(status_code=404, detail="Archivo no encontrado en portafolio.")
    if safe_target.endswith(".html"):
        rel_dir = os.path.relpath(os.path.dirname(safe_target), base_abs).replace(os.sep, "/")
        dir_prefix = prefix if rel_dir in ("", ".") else f"{prefix}{rel_dir.strip('/')}/"
        with open(safe_target, "r", encoding="utf-8", errors="replace") as f:
            content = _inject_base_href(f.read(), dir_prefix)
        return HTMLResponse(content=content)
    return FileResponse(safe_target)


def _rewrite_jinja_html(html_text: str, slug: str, routes_to_prefix: list[str]) -> str:
    """Reescribe enlaces /static/ y rutas raíz internas hacia /portafolio-vivo/{slug}/."""
    base = f"/portafolio-vivo/{slug}"
    html_text = html_text.replace('"/static/', f'"{base}/static/').replace("'/static/", f"'{base}/static/")
    html_text = re.sub(r'href="/(?:\?lang=([^"]*))?"', lambda m: f'href="{base}/' + (f'?lang={m.group(1)}' if m.group(1) else '') + '"', html_text)
    for r in routes_to_prefix:
        clean_r = r.lstrip("/")
        html_text = html_text.replace(f'href="/{clean_r}', f'href="{base}/{clean_r}')
    return html_text


def setup_portafolio_vivo(app: FastAPI) -> None:
    """Monta archivos estáticos y registra rutas del portafolio vivo en la app principal."""
    # Montar assets de Blancos Girasol si existen en el entorno local
    if BLANCOS_DIST_DIR and os.path.isdir(os.path.join(BLANCOS_DIST_DIR, "assets")):
        app.mount(
            "/assets",
            StaticFiles(directory=os.path.join(BLANCOS_DIST_DIR, "assets")),
            name="blancos_root_assets",
        )
        for sub in ("extracted_images", "lovable-uploads"):
            sub_dir = os.path.join(BLANCOS_DIST_DIR, sub)
            if os.path.isdir(sub_dir):
                app.mount(f"/{sub}", StaticFiles(directory=sub_dir), name=f"blancos_{sub}")

    # Montar estáticos de las apps Jinja2 locales
    if JPX_DIR and os.path.isdir(os.path.join(JPX_DIR, "static")):
        app.mount(
            "/portafolio-vivo/jpxinternational/static",
            StaticFiles(directory=os.path.join(JPX_DIR, "static")),
            name="jpx_portfolio_static",
        )
    if SUNOTARIA_DIR and os.path.isdir(os.path.join(SUNOTARIA_DIR, "static")):
        app.mount(
            "/portafolio-vivo/sunotariausa/static",
            StaticFiles(directory=os.path.join(SUNOTARIA_DIR, "static")),
            name="sunotaria_portfolio_static",
        )
    if SYNETCOM_DIR and os.path.isdir(os.path.join(SYNETCOM_DIR, "static")):
        app.mount(
            "/portafolio-vivo/synetcom/static",
            StaticFiles(directory=os.path.join(SYNETCOM_DIR, "static")),
            name="synetcom_portfolio_static",
        )

    app.include_router(router)


# ─── BLANCOS GIRASOL (SPA REACT/VITE) ────────────────────────────────────────
@router.get("/portafolio-vivo/blancosgirasol")
@router.get("/portafolio-vivo/blancosgirasol/")
@router.get("/portafolio-vivo/blancosgirasol/{rest:path}")
async def serve_blancos_girasol(rest: str = ""):
    if not BLANCOS_DIST_DIR:
        return RedirectResponse("https://blancosgirasol.com/", status_code=307)
    clean = rest.lstrip("/")
    if clean and "." in os.path.basename(clean):
        target = os.path.abspath(os.path.join(BLANCOS_DIST_DIR, clean))
        if target.startswith(os.path.abspath(BLANCOS_DIST_DIR)) and os.path.isfile(target):
            return FileResponse(target)
    index_file = os.path.join(BLANCOS_DIST_DIR, "index.html")
    if not os.path.isfile(index_file):
        return RedirectResponse("https://blancosgirasol.com/", status_code=307)
    with open(index_file, "r", encoding="utf-8", errors="replace") as f:
        html = f.read()
    # Asegurar que BrowserRouter resuelva '/' al abrir la vista previa
    spa_shim = "<script>if(window.location.pathname.indexOf('/portafolio-vivo/blancosgirasol')===0){try{window.history.replaceState(null,'','/');}catch(e){}}</script>"
    html = re.sub(r"(<head[^>]*>)", rf"\1\n  {spa_shim}", html, count=1, flags=re.IGNORECASE)
    return HTMLResponse(content=html)


# ─── JPX INTERNATIONAL (JINJA2) ──────────────────────────────────────────────
def _render_jpx(request: Request, template_name: str, active_page: str):
    if not JPX_DIR:
        return RedirectResponse("/demo-sitio-web?template=profesionales_consultoria_legal", status_code=307)
    tpl_dir = os.path.join(JPX_DIR, "templates")
    if not os.path.isdir(tpl_dir):
        return RedirectResponse("/demo-sitio-web?template=profesionales_consultoria_legal", status_code=307)
    jpx_tpl = Jinja2Templates(directory=tpl_dir)
    lang = request.query_params.get("lang") or "es"

    def jpx_static(path: str) -> str:
        return f"/portafolio-vivo/jpxinternational/static/{path.lstrip('/')}"

    jpx_tpl.env.globals["static_versioned"] = jpx_static
    rendered = jpx_tpl.TemplateResponse(
        request=request,
        name=template_name,
        context={"lang": lang, "active_page": active_page},
    ).body.decode("utf-8", errors="replace")
    rendered = _rewrite_jinja_html(rendered, "jpxinternational", ["firma", "servicios", "commodities", "consultoria", "contacto"])
    return HTMLResponse(content=rendered)


@router.get("/portafolio-vivo/jpxinternational")
@router.get("/portafolio-vivo/jpxinternational/")
async def serve_jpx_index(request: Request):
    return _render_jpx(request, "index.html", "index")


@router.get("/portafolio-vivo/jpxinternational/{page}")
async def serve_jpx_subpage(request: Request, page: str):
    allowed = {"firma": "firma.html", "servicios": "servicios.html", "commodities": "commodities.html", "consultoria": "consultoria.html", "contacto": "contacto.html"}
    tpl = allowed.get(page, "index.html")
    return _render_jpx(request, tpl, page if page in allowed else "index")


# ─── SU NOTARIA USA (JINJA2) ─────────────────────────────────────────────────
def _render_sunotaria(request: Request, template_name: str, active_page: str, lang: str = "es"):
    if not SUNOTARIA_DIR:
        return RedirectResponse("/demo-sitio-web?template=profesionales_consultoria_legal", status_code=307)
    tpl_dir = os.path.join(SUNOTARIA_DIR, "templates")
    if not os.path.isdir(tpl_dir):
        return RedirectResponse("/demo-sitio-web?template=profesionales_consultoria_legal", status_code=307)
    sn_tpl = Jinja2Templates(directory=tpl_dir)

    def sn_static(path: str) -> str:
        return f"/portafolio-vivo/sunotariausa/static/{path.lstrip('/')}"

    def sn_traducir(url_path: str, target_lang: str) -> str:
        base = "/portafolio-vivo/sunotariausa"
        return f"{base}/en" if target_lang == "en" else f"{base}/"

    sn_tpl.env.globals["static_versioned"] = sn_static
    sn_tpl.env.globals["traducir_url"] = sn_traducir
    rendered = sn_tpl.TemplateResponse(
        request=request,
        name=template_name,
        context={"lang": lang, "active_page": active_page},
    ).body.decode("utf-8", errors="replace")
    rendered = _rewrite_jinja_html(rendered, "sunotariausa", ["en", "servicios", "contacto", "privacidad", "terminos"])
    return HTMLResponse(content=rendered)


@router.get("/portafolio-vivo/sunotariausa")
@router.get("/portafolio-vivo/sunotariausa/")
async def serve_sunotaria_index(request: Request):
    return _render_sunotaria(request, "index.html", "index", "es")


@router.get("/portafolio-vivo/sunotariausa/{page:path}")
async def serve_sunotaria_subpage(request: Request, page: str):
    clean = page.strip("/")
    lang = "en" if clean == "en" or clean.startswith("en/") else "es"
    sub = clean[3:] if clean.startswith("en/") else ("" if clean == "en" else clean)
    allowed = {"": "index.html", "servicios": "servicios.html", "contacto": "contacto.html", "privacidad": "privacidad.html", "terminos": "terminos.html"}
    tpl = allowed.get(sub.split("/")[0], "index.html")
    return _render_sunotaria(request, tpl, sub.split("/")[0] or "index", lang)


# ─── SYNETCOM (JINJA2) ───────────────────────────────────────────────────────
def _render_synetcom(request: Request, page_file: str = "index.html"):
    if not SYNETCOM_DIR:
        return RedirectResponse("/demo-sitio-web?template=sti2q_industrial", status_code=307)
    tpl_dir = os.path.join(SYNETCOM_DIR, "templates")
    if not os.path.isdir(tpl_dir):
        return RedirectResponse("/demo-sitio-web?template=sti2q_industrial", status_code=307)
    syn_tpl = Jinja2Templates(directory=tpl_dir)

    def syn_url_for(name: str, **kwargs) -> str:
        if name == "static":
            return f"/portafolio-vivo/synetcom/static/{str(kwargs.get('path', '')).lstrip('/')}"
        return f"/portafolio-vivo/synetcom/{name}"

    syn_tpl.env.globals["url_for"] = syn_url_for
    allowed = {
        "index.html": "inicio",
        "acerca.html": "acerca",
        "camaras.html": "camaras",
        "conectividad-empresarial.html": "conectividad",
        "contacto.html": "contacto",
        "inteligencia-artificial.html": "ia",
        "soporte.html": "soporte",
        "aviso-privacidad.html": "privacidad",
        "politica-cookies.html": "cookies",
        "terminos-condiciones.html": "terminos",
    }
    if page_file not in allowed:
        page_file = "index.html"
    rendered = syn_tpl.TemplateResponse(
        request=request,
        name=page_file,
        context={"page_name": allowed[page_file]},
    ).body.decode("utf-8", errors="replace")
    rendered = _inject_base_href(rendered, "/portafolio-vivo/synetcom/")
    return HTMLResponse(content=rendered)


@router.get("/portafolio-vivo/synetcom")
@router.get("/portafolio-vivo/synetcom/")
async def serve_synetcom_index(request: Request):
    return _render_synetcom(request, "index.html")


@router.get("/portafolio-vivo/synetcom/{page_name}")
async def serve_synetcom_page(request: Request, page_name: str):
    if not page_name.endswith(".html"):
        page_name = f"{page_name}.html"
    return _render_synetcom(request, page_name)


# ─── SITIOS ESTÁTICOS PUROS (SERVIXO, DORAL, IDOLJOSE, ESENCIA, EDWARD) ─────
@router.get("/portafolio-vivo/{slug}")
@router.get("/portafolio-vivo/{slug}/")
@router.get("/portafolio-vivo/{slug}/{subpath:path}")
async def serve_static_portfolio(slug: str, subpath: str = ""):
    entry = STATIC_PORTFOLIO_MAP.get(slug)
    if not entry:
        raise HTTPException(status_code=404, detail="Sitio de portafolio no encontrado.")
    site_dir = entry.get("dir")
    if not site_dir or not os.path.isdir(site_dir):
        return RedirectResponse(entry["fallback_url"] or "/paginas-web", status_code=307)
    return _serve_static_site_file(site_dir, f"/portafolio-vivo/{slug}/", subpath)
