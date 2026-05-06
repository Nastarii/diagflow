"""Minimal example: single step, 3 nodes, one message."""
from diagflow import Diagram, Node

d = Diagram("Hello Diagflow")

api = Node("API")
db  = Node("Database")

d.add(api, db)
edge = d.connect(api, db, label="SQL")

d.animate(
    api.fade_in(),
    db.fade_in(at=0.4),
    edge.fade_in(at=0.7),
    api.send("SELECT * FROM users", db, at=1.1),
)

d.export("examples/basic_output.html")
