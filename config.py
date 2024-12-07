import os

# Default SPARQL endpoint for local testing
SPARQL_ENDPOINT = os.getenv("SPARQL_ENDPOINT",
                            "http://http://40.90.195.237:7200/repository/GothamWatch")
