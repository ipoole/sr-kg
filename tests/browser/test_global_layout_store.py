"""Published/personal positions must remain independent of temporary graph moves."""
from pathlib import Path
import pytest


@pytest.mark.browser
def test_layout_store_owns_positions_coalesces_saves_and_cancels_on_reset(playwright_browser):
    _, browser = playwright_browser
    page = browser.new_page()
    try:
        assets = Path(__file__).resolve().parents[2] / 'srkg/viewer_assets'
        for name in ('layout_geometry.js', 'global_layout.js'):
            page.add_script_tag(path=str(assets / name))
        page.evaluate("""() => {
          window.writes = [];
          window.positions = [{id:'a',x:100,y:200}];
          window.layout = kgCreateGlobalLayout({
            publishedLayout:{schema_version:1,revision:'r1',concepts:{a:{x:10,y:20}},modules:{}},
            getNodes:()=>positions, nodes:{get:()=>positions[0],update:()=>{}},
            store:{getLayoutState:()=>null,replaceLayout:value=>writes.push(value)},
            storageKey:'layout',storage:{set:()=>true,remove:()=>true},
            onStatusChange:()=>{},onSave:()=>{},beforeReset:()=>{},onPositionsApplied:()=>{}
          });
          positions[0].x=999; // A temporary canvas move must not become a saved position.
          const copy=layout.globalLayoutSnapshot(); copy.concepts.a.x=-1;
        }""")
        assert page.evaluate("layout.globalLayoutSnapshot().concepts.a") == {'x': 10, 'y': 20}
        page.evaluate("""() => {
          layout.setGlobalConceptPosition('a',{x:30,y:40});
          layout.setGlobalConceptPosition('a',{x:50,y:60});
        }""")
        page.wait_for_function('writes.length === 1')
        assert page.evaluate('writes[0].concepts.a') == {'x': 50, 'y': 60}
        page.evaluate("""() => {
          layout.setGlobalConceptPosition('a',{x:70,y:80});
          layout.resetToPublishedLayout();
        }""")
        page.wait_for_timeout(160)
        assert page.evaluate('writes.length') == 2
        assert page.evaluate('layout.globalLayoutSnapshot().concepts.a') == {'x': 10, 'y': 20}
        assert page.evaluate('writes[1].concepts') == {}
    finally:
        page.close()
