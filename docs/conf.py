project = "python-arango"
copyright = "2016-2022, Joohwan Oh"
author = "Joohwan Oh"
extensions = [
    "sphinx_rtd_theme",
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.viewcode",
]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
html_static_path = ["static"]
html_theme = "sphinx_rtd_theme"
master_doc = "index"

autodoc_member_order = "bysource"

doctest_global_setup = """
from arango import ArangoClient
# Initialize the ArangoDB client.
client = ArangoClient()
# Connect to "_system" database as root user.
sys_db = client.db('_system', username='root', password='passwd')
# Create "test" database if it does not exist.
if not sys_db.has_database('test'):
    sys_db.create_database('test')
# Ensure that user "johndoe@gmail.com" does not exist.
if sys_db.has_user('johndoe@gmail.com'):
    sys_db.delete_user('johndoe@gmail.com')
# Connect to "test" database as root user.
db = client.db('test', username='root', password='passwd')
# Create "students" collection if it does not exist.
if db.has_collection('students'):
    db.collection('students').truncate()
else:
    db.create_collection('students')
# Ensure that "cities" collection does not exist.
if db.has_collection('cities'):
    db.delete_collection('cities')
# Create "school" graph if it does not exist.
if db.has_graph("school"):
    school = db.graph('school')
else:
    school = db.create_graph('school')
# Create "teachers" vertex collection if it does not exist.
if school.has_vertex_collection('teachers'):
    school.vertex_collection('teachers').truncate()
else:
    school.create_vertex_collection('teachers')
# Create "lectures" vertex collection if it does not exist.
if school.has_vertex_collection('lectures'):
    school.vertex_collection('lectures').truncate()
else:
    school.create_vertex_collection('lectures')
# Create "teach" edge definition if it does not exist.
if school.has_edge_definition('teach'):
    school.edge_collection('teach').truncate()
else:
    school.create_edge_definition(
        edge_collection='teach',
        from_vertex_collections=['teachers'],
        to_vertex_collections=['lectures']
    )
"""
