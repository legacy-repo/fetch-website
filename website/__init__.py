from website import expression_atlas
from website import gtexportal
from website import sanger_cosmic

websites = {
    "expression_atlas": expression_atlas,
    "gtexportal": gtexportal,
    "sanger_cosmic": sanger_cosmic,
}

blueprints = [
    {
        "name": "gxa",
        "url_prefix": "/gxa",
        "blueprint": expression_atlas.subroute_blueprint,
    },
    {
        "name": "sanger_cosmic",
        "url_prefix": "/sanger_cosmic",
        "blueprint": sanger_cosmic.subroute_blueprint,
    },
    {
        "name": "gtexportal",
        "url_prefix": "/gtex",
        "blueprint": gtexportal.subroute_blueprint,
    },
]
