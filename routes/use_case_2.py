from flask import Blueprint, request, jsonify
from utils.sparql_helper import query_sparql

use_case_2_bp = Blueprint("use_case_2", __name__)

@use_case_2_bp.route("/use-case-2", methods=["POST"])
def use_case_2():
    data = request.json
    selected_state = data.get("selectedState", "")
    print(data, selected_state)
    sparql_query = f"""
    PREFIX smw: <http://www.semanticweb.org/ser531/ontologies/crimeStatistics#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?countyName ?countyCode
    WHERE {{
      ?state smw:hasCounty ?county .
      ?county smw:hasCountyName ?countyName .

      # Extract the county code from the URI
      BIND(STRAFTER(STR(?county), "#") AS ?countyCode)

      FILTER(?state = smw:{selected_state})
    }}
    """

    try:
        print("Constructed SPARQL Query:\n", sparql_query)
        raw_results = query_sparql(sparql_query)

        if not raw_results.get("results") or not raw_results["results"].get("bindings"):
            print("No results or invalid response structure")
            return jsonify({"error": "No results match your query. Please adjust the state filter."}), 404

        parsed_results = []
        for result in raw_results["results"]["bindings"]:
            county_name = result.get("countyName", {}).get("value", "N/A")
            county_code = result.get("countyCode", {}).get("value", "N/A")

            parsed_results.append({
                "label": county_name,
                "value": county_code,
            })

        return jsonify({"results": parsed_results})

    except Exception as e:
        print("Error executing SPARQL query:", str(e))
        return jsonify({"error": str(e)}), 500
