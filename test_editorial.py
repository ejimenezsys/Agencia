from editorial import enrich_post
from editorial_workflow import validate
from database import hash_password, verify_password


def sample_post(**overrides):
    post = {
        "slug": "una-senal-que-cambia-decisiones",
        "title": "Una señal tecnológica que cambia decisiones",
        "summary": "Un resumen ejecutivo suficientemente amplio para explicar el valor de la pieza.",
        "content": "<p>" + ("criterio empresarial " * 40) + "</p>",
        "lane": "radar-disrupcion",
        "author": "Equipo editorial ProsperIA",
        "author_type": "organization",
        "status": "draft",
        "sources": [{"title": "Fuente primaria", "url": "https://example.org/report"}],
        "cta": "diagnostic",
    }
    post.update(overrides)
    return post


def test_legacy_post_is_enriched_without_inventing_sources():
    post = enrich_post({"category": "Operaciones", "content": "palabra " * 420, "author": "Prosper IA"})
    assert post["lane"] == "laboratorio-prosperia"
    assert post["sources"] == []
    assert post["reading_minutes"] == 2


def test_unapproved_legacy_personal_byline_becomes_editorial():
    post = enrich_post({"category": "Operaciones", "content": "texto", "author": "Edward Jiménez"})
    assert post["author"] == "Equipo editorial ProsperIA"
    assert post["author_type"] == "organization"
    assert post["original_author"] == "Edward Jiménez"


def test_new_post_requires_human_review_before_publication():
    errors = validate(sample_post(), publish=True)
    assert "Solo un artículo aprobado puede publicarse." in errors
    assert "Falta reviewed_by." in errors


def test_edward_byline_requires_explicit_approval():
    errors = validate(sample_post(status="approved", reviewed_by="Editora", author="Edward Jiménez"), publish=True)
    assert "Edward debe aprobar expresamente los textos firmados con su nombre." in errors


def test_approved_sourced_organization_post_can_publish():
    assert validate(sample_post(status="approved", reviewed_by="Editora"), publish=True) == []


def test_passwords_are_hashed_and_verified():
    encoded = hash_password("una-frase-segura")
    assert encoded != "una-frase-segura"
    assert verify_password("una-frase-segura", encoded)
    assert not verify_password("otra-frase", encoded)
