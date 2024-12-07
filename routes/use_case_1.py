from flask import Blueprint, jsonify
from utils.sparql_helper import query_sparql

use_case_1_bp = Blueprint("use_case_1", __name__)


@use_case_1_bp.route("/use-case-1", methods=["POST"])
def use_case_1():
    print('Api called')
    sparql_query = """
    PREFIX smw: <http://www.semanticweb.org/ser531/ontologies/crimeStatistics#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?stateName ?stateCode
    WHERE {
      ?state a smw:State ;
             smw:hasStateName ?stateName .
      
      # Extract the state code from the URI
      BIND(STRAFTER(STR(?state), "#") AS ?stateCode)
    }
    ORDER BY ?stateName
    """

    try:
        raw_results = query_sparql(sparql_query)

        parsed_results = [
            {
                "label": result["stateName"]["value"],
                "value": result["stateCode"]["value"]
            }
            for result in raw_results["results"]["bindings"]
        ]

        return jsonify(parsed_results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
