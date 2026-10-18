from pathlib import Path
import struct


ROOT = Path(__file__).resolve().parents[1]


def _page(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


def test_public_homepage_identifies_physicskg_and_links_required_pages():
    homepage = _page("index.html")

    assert "PhysicsKG" in homepage
    assert "An Atlas of Physics Knowledge" in homepage
    assert "Study physics through visually connected concepts" in homepage
    assert 'href="output/PhysicsKG.html"' in homepage
    assert 'href="privacy.html"' in homepage
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


def test_google_branding_logo_is_a_120_pixel_png():
    logo = ROOT / "physicskg-logo-120.png"
    content = logo.read_bytes()

    assert content[:8] == b"\x89PNG\r\n\x1a\n"
    width, height = struct.unpack(">II", content[16:24])
    assert (width, height) == (120, 120)


def test_viewer_offers_a_public_privacy_policy_link():
    controls = (ROOT / "srkg/viewer_assets/controls.html").read_text(encoding="utf-8")

    assert 'href="https://ipoole.github.io/sr-kg/privacy.html"' in controls
    assert "Privacy and Google Drive data use" in controls
