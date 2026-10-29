from pathlib import Path
import struct
from html.parser import HTMLParser
from xml.etree import ElementTree

from srkg.branding import PRODUCT_VERSION


ROOT = Path(__file__).resolve().parents[1]


def _canonical_urls(html):
    class Links(HTMLParser):
        urls = []

        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if tag == "link" and attrs.get("rel") == "canonical":
                self.urls.append(attrs.get("href"))

    parser = Links()
    parser.feed(html)
    return parser.urls


def test_public_pages_and_viewer_declare_preferred_https_urls():
    from srkg.html_injection import inject_controls

    for page, url in (
        ("index.html", "https://physicskg.org/"),
        ("privacy.html", "https://physicskg.org/privacy.html"),
        ("terms.html", "https://physicskg.org/terms.html"),
    ):
        assert _canonical_urls(_page(page)) == [url]
    viewer = inject_controls("<html><head></head><body></body></html>", {}, {}, "Title")
    assert _canonical_urls(viewer) == ["https://physicskg.org/output/PhysicsKG.html"]


def test_sitemap_lists_only_preferred_public_pages_and_is_discoverable():
    sitemap = ElementTree.parse(ROOT / "sitemap.xml")
    urls = [node.text for node in sitemap.findall("{*}url/{*}loc")]
    assert sorted(urls) == sorted([
        "https://physicskg.org/",
        "https://physicskg.org/output/PhysicsKG.html",
        "https://physicskg.org/privacy.html",
        "https://physicskg.org/terms.html",
    ])
    assert "Sitemap: https://physicskg.org/sitemap.xml" in _page("robots.txt").splitlines()


def _page(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


def test_public_homepage_identifies_physicskg_and_links_required_pages():
    homepage = _page("index.html")

    assert "PhysicsKG" in homepage
    assert "An Atlas of Physics Knowledge" in homepage
    assert "Study physics through visually connected concepts" in homepage
    assert 'href="output/PhysicsKG.html"' in homepage
    assert 'href="output/PhysicsKG.html?tutorial=using-physicskg"' in homepage
    assert "Launch guided tutorial" in homepage
    assert 'href="privacy.html"' in homepage
    assert 'href="terms.html"' in homepage
    assert "Google Drive" in homepage
    assert "drive.file" in homepage


def test_privacy_policy_discloses_personal_and_google_data_handling():
    policy = _page("privacy.html")
    normalised_policy = " ".join(policy.split())

    assert (
        "PhysicsKG does not operate an application server, and personal data "
        "is not accessible to the developer through PhysicsKG."
    ) in normalised_policy
    for disclosure in (
        "PhysicsKG personal data.zip",
        "browser's local storage",
        "drive.file",
        "access token",
        "does not operate an application server",
        "Google Drive",
        "delete",
    ):
        assert disclosure in policy


def test_public_terms_cover_educational_use_and_optional_drive_service():
    terms = _page("terms.html")

    assert "Terms of service" in terms
    assert "educational" in terms
    assert "as is" in terms
    assert "Google Drive" in terms
    assert 'href="privacy.html"' in terms


def test_google_branding_logo_is_a_120_pixel_png():
    logo = ROOT / "physicskg-logo-120.png"
    content = logo.read_bytes()

    assert content[:8] == b"\x89PNG\r\n\x1a\n"
    width, height = struct.unpack(">II", content[16:24])
    assert (width, height) == (120, 120)


def test_viewer_offers_a_public_privacy_policy_link():
    controls = (ROOT / "srkg/viewer_assets/controls.html").read_text(encoding="utf-8")

    assert 'href="https://physicskg.org/privacy.html"' in controls
    assert "Privacy and Google Drive data use" in controls


def test_product_version_is_four_point_two_point_zero():
    assert PRODUCT_VERSION == "4.2.1"
    assert all(part.isdigit() for part in PRODUCT_VERSION.split("."))
