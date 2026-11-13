"""Real SR field content fits both panes and its trees follow stored dependencies."""
import csv
import pytest
from conftest import REPO_ROOT,_open_browser_graph
from test_sr1_reading_content import sr1_reading_output
from test_maths_reading_trees import _reveal_tree
MODULES=[('sr.variational_and_field_theory','sr.field_equations'),('sr.electromagnetic_structure_gauge_and_stress_energy','sr.lorentz_force_law'),('sr.field_dynamics_conservation_and_radiation','sr.radiation_reaction')]
@pytest.mark.browser
@pytest.mark.browser_full
@pytest.mark.parametrize('module,root',MODULES)
@pytest.mark.parametrize('width',[390,1280],ids=['phone','desktop'])
def test_field_module_content_and_reading_routes(sr1_reading_output,playwright_browser,module,root,width):
 with (REPO_ROOT/'domains/sr/data/module_members.csv').open() as source:
  owners=[r['concept_id'] for r in csv.DictReader(source) if r['module_id']==module]
 api,browser=playwright_browser
 with _open_browser_graph(api,browser,sr1_reading_output,{'viewport':{'width':width,'height':900}}) as graph:
  page=graph.page;page.locator('#kg_view_select').select_option('details')
  for owner in owners:
   graph.click_concept(owner)
   blocks=page.locator('#info_panel > .content-block')
   assert blocks.locator(':scope > summary .kg-content-statement').count()==blocks.locator(':scope:not(.content-block-graphic)').count()
   blocks.evaluate_all('es=>es.forEach(e=>e.open=true)')
   page.locator('#info_panel .kg-local-explanation').evaluate_all('es=>es.forEach(e=>e.open=true)')
   page.wait_for_function('window.MathJax && typeof MathJax.typesetPromise==="function"')
   page.evaluate('MathJax.startup.promise');page.evaluate('MathJax.typesetPromise([document.getElementById("info_panel")])')
   assert not page.locator('#info_panel mjx-merror,#info_panel [data-mjx-error]').count(),owner
   assert page.locator('#info_panel').evaluate('e=>e.scrollWidth<=e.clientWidth+1'),owner
   assert blocks.locator('mjx-container[display="true"]').evaluate_all('es=>es.every(e=>!e.clientWidth||e.scrollWidth<=e.clientWidth+2)'),owner
   assert page.locator('#info_panel .concept-graphic').count()==1
  graph.click_concept(root)
  for recipe,preset in [('derivation','derivation'),('teaching','foundations')]:
   card=page.locator(f'details.kg-reading-tree[data-reading-recipe="{recipe}"]')
   # The SR field chain is deeper than the Maths pilot. An acyclic path cannot
   # exceed the loaded concept count; retain that finite guard when unfolding.
   _reveal_tree(page,card,max_depth=page.evaluate('Object.keys(conceptData).length'),
                unique_concepts=True)
   expected=page.evaluate('(a)=>kgComputeContext({type:"concept",id:a.root},{preset:a.preset,depth:"transitive"})',{'root':root,'preset':preset})
   actual=card.locator('[data-reading-edge]').evaluate_all('es=>[...new Set(es.map(e=>e.dataset.readingEdge))]')
   assert set(actual)==set(expected['edgeIds'])
   assert not card.locator('.kg-reading-block[open]').count()
   card.evaluate('e=>e.open=false')
  assert not graph.page_errors
