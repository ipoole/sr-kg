"""Declarative tutorial command/field contract shared by Python and the editor."""

TUTORIAL_CATEGORIES = frozenset({"interface", "physics"})
TOOLS_SECTIONS = frozenset({
    "tutorials",
    "modules",
    "layouts",
    "study",
    "personal-data",
    "notes",
})
READING_TREE_RECIPES = frozenset({"derivation", "teaching"})
TUTORIAL_EDGE_RELATIONS = frozenset({
    "REQUIRES",
    "DERIVES_FROM",
    "CONSTRUCTED_FROM",
    "COMPONENT_OF",
    "INSTANCE_OF",
    "RELATED",
})
CONTROL_TARGETS = frozenset({
    "context",
    "depth",
    "fit",
    "display-scope",
    "view",
    "search",
    "search-input",
    "tools",
    "expand-context",
})



def field(name, label, kind, **options):
    return dict(name=name, label=label, type=kind, **options)


def choice(name, label, values, default=None, **options):
    values = dict(values) if isinstance(values, list) else dict.fromkeys(sorted(values))
    values = {key: value or key.replace('-', ' ').capitalize() for key, value in values.items()}
    return field(name, label, 'enum', choices=values, default=default or next(iter(values)), **options)


def command(label, *fields, pointer='narration'):
    return dict(label=label, fields=list(fields), pointer=pointer)


CONTEXT_CHOICES = [('derivation', 'Derivation'), ('foundations', 'Foundations'),
    ('prerequisites', 'Prerequisites'), ('uses', 'Uses'), ('connections', 'Connections'), ('related', 'Related')]
DEPTH_CHOICES = [('one-hop', '1 hop'), ('two-hops', '2 hops'), ('three-hops', '3 hops'), ('transitive', 'Full tree')]
RELATIONSHIP_CHOICES = [('derived-from', 'Derived from'), ('where-used', 'Where used')]
COMMANDS = {
    'home': command('Restore the starting view'),
    'select': command('Select a concept or module', field('target', 'Selection', 'object'), pointer='graph:{target}'),
    'set-display-scope': command('Choose graph mode', choice('value', 'Graph mode', [
        ('overview', 'Overview'), ('full', 'Context + background'), ('context', 'Context only')]), pointer='control:display-scope'),
    'set-context': command('Choose context and depth', choice('preset', 'Context', CONTEXT_CHOICES),
        choice('depth', 'Depth', DEPTH_CHOICES, 'two-hops'), pointer='control:context'),
    'set-view': command('Choose visible panes', choice('value', 'View', [
        ('both', 'Both'), ('graph', 'Graph only'), ('details', 'Details only')]), pointer='control:view'),
    'set-module-representation': command('Expand or fold a module', field('target', 'Module', 'module'),
        choice('value', 'Representation', [('expanded', 'Expanded'), ('folded', 'Folded')]), pointer='control:module-fold:{target_id}'),
    'set-all-module-representations': command('Expand or fold all modules',
        choice('value', 'Representation', [('expanded', 'Expanded'), ('folded', 'Folded')]), pointer='tools:section:modules'),
    'expand-context-modules': command('Expand context modules', pointer='control:expand-context'),
    'fit': command('Fit the graph', choice('value', 'Frame', [
        ('context', 'Context (repeat for Fit++)'), ('displayed', 'All displayed'),
        ('selection', 'Selection'), ('reveal', 'Reveal selection')]), pointer='control:fit'),
    'open-details-block': command('Open a content block', field('target', 'Content block', 'block'), field('open', 'Open (optional)', 'boolean', optional=True), pointer='details:{target}'),
    'open-reading-tree': command('Open a reading tree', choice('recipe', 'Recipe', READING_TREE_RECIPES, 'teaching'),
        field('target', 'Support concept (optional)', 'concept', optional=True),
        choice('depth', 'Depth (optional)', DEPTH_CHOICES, optional=True),
        field('synchronise', 'Synchronise graph (optional)', 'boolean', optional=True),
        field('block', 'Reading block (optional)', 'block', optional=True),
        field('open', 'Open (optional)', 'boolean', optional=True), pointer='details:reading-tree:{recipe}'),
    'open-study-questions': command('Open Study Questions', field('open', 'Open (optional)', 'boolean', optional=True), pointer='details:study-questions'),
    'open-details-graphic': command('Open the main graphic', field('open', 'Open (optional)', 'boolean', optional=True), pointer='details:graphic'),
    'open-details-relationship': command('Open a relationship section', choice('value', 'Section', RELATIONSHIP_CHOICES), field('open', 'Open (optional)', 'boolean', optional=True), pointer='details:heading'),
    'set-relationship-full-tree': command('Change relationship tree depth', choice('value', 'Section', RELATIONSHIP_CHOICES),
        field('full_tree', 'Show full tree', 'boolean', default=True), pointer='details:{value}-full-tree'),
    'show-relationship-in-graph': command('Show relationships in the graph', choice('preset', 'Context', CONTEXT_CHOICES),
        field('full_tree', 'Show full tree', 'boolean', default=False), pointer='details:derived-from-show-graph'),
    'show-graph-concept-hover': command('Show concept hover information', field('target', 'Concept', 'concept'), pointer='graph:{target}'),
    'show-graph-edge-hover': command('Show edge hover information', field('target', 'Edge', 'edge'), pointer='graph:{target}'),
    'show-tools-section': command('Open a Tools section', choice('value', 'Section', TOOLS_SECTIONS), pointer='tools:section:{value}'),
    'search': command('Search concepts and modules', field('query', 'Search text', 'text', max_length=200, allow_empty=True), pointer='control:search-input'),
    'close-search': command('Close Search', pointer='control:search'),
    'wait': command('Wait briefly', field('milliseconds', 'Wait (seconds)', 'integer', min=0, max=5000, default=500, scale=1000)),
}
TUTORIAL_COMMANDS = frozenset(COMMANDS)
POINTER_BASE_TARGETS = dict([('narration', 'Narration only'), ('details:heading', 'Details heading'),
    ('details:contents', 'Contents'), ('details:study-questions', 'Study Questions'), ('details:graphic', 'Main graphic'),
    ('details:derived-from-show-graph', 'Derived from: Show in graph'), ('details:where-used-show-graph', 'Where used: Show in graph'),
    ('details:derived-from-full-tree', 'Derived from: Full tree'), ('details:where-used-full-tree', 'Where used: Full tree')])


def authoring_contract():
    return dict(commands=COMMANDS, max_actions=20, max_pause_ms=5000,
        pointer_base=POINTER_BASE_TARGETS, controls=sorted(CONTROL_TARGETS),
        recipes=sorted(READING_TREE_RECIPES), tools=sorted(TOOLS_SECTIONS), relations=sorted(TUTORIAL_EDGE_RELATIONS))
