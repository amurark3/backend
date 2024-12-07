from flask import Blueprint, request, jsonify
from utils.sparql_helper import query_sparql

use_case_3_bp = Blueprint("use_case_3", __name__)

@use_case_3_bp.route("/use-case-3", methods=["POST"])
def use_case_3():
    data = request.json
    selected_state = data.get("selectedState", "")
    selected_county = data.get("selectedCounty", "")
    selected_year = data.get("selectedYear", "")

    crime_name_mapping = {
        "AGASSLT": "Aggravated Assault",
        "DUI": "DUI",
        "FRAUD": "Fraud",
        "MURDER": "Murder",
        "RAPE": "Rape",
        "ROBBERY": "Robbery",
        "WEAPONS": "Weapons"
    }

    sparql_query = f"""
    PREFIX smw: <http://www.semanticweb.org/ser531/ontologies/crimeStatistics#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?crimeCategoryName ?frequency
    WHERE {{
      ?state smw:hasCounty ?county .
      ?county smw:hasCrimeYear ?crimeYear .
      
      # Filter by specific state and county codes
      FILTER(STRAFTER(STR(?state), "#") = "{selected_state}")
      FILTER(STRAFTER(STR(?county), "#") = "{selected_county}")
      
      # Filter by a specific year
      FILTER(CONTAINS(STR(?crimeYear), "{selected_year}"))
      
      ?crimeYear smw:hasCrimeCategory ?crimeCategory .
      ?crimeCategory rdfs:label ?crimeCategoryName ;
                     smw:hasFrequency ?frequency .
    }}
    ORDER BY ?crimeCategoryName
    """

    try:
        print("Constructed SPARQL Query:\n", sparql_query)
        raw_results = query_sparql(sparql_query)

        if not raw_results.get("results") or not raw_results["results"].get("bindings"):
            print("No results or invalid response structure")
            return jsonify({"error": "No results match your query. Please adjust the filters."}), 404

        # Create the result list with headers
        processed_data = [['Crime Name', 'Number of crimes']]

        for result in raw_results["results"]["bindings"]:
            crime_code = result.get("crimeCategoryName", {}).get("value", "")
            frequency = result.get("frequency", {}).get("value", "")

            try:
                num_crimes = int(frequency.split('_')[-1])

                crime_name = crime_name_mapping.get(crime_code, crime_code)

                processed_data.append([crime_name, num_crimes])
            except ValueError:
                print(f"Error processing frequency for {crime_code}: {frequency}")

        return jsonify({"results": processed_data})

    except Exception as e:
        print("Error executing SPARQL query:", str(e))
        return jsonify({"error": str(e)}), 500
