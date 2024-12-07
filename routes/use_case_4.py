from flask import Blueprint, request, jsonify
from utils.sparql_helper import query_sparql

use_case_4_bp = Blueprint("use_case_4", __name__)

@use_case_4_bp.route("/use-case-4", methods=["POST"])
def use_case_4():
    data = request.json
    years = data.get("years", [])
    if not years:
        return jsonify({"error": "At least one year must be provided."}), 400

    year_filter = " || ".join([f'CONTAINS(STR(?crimeYear), "{year}")' for year in years])

    sparql_query = f"""
    PREFIX smw: <http://www.semanticweb.org/ser531/ontologies/crimeStatistics#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?countyName ?fipsCode 
           (GROUP_CONCAT(DISTINCT ?frequency; separator=", ") AS ?frequencies)
    WHERE {{
      ?county smw:hasCountyName ?countyName ;
              smw:hasFIPSCode ?fipsCode ;
              smw:hasCrimeYear ?crimeYear .

      ?crimeYear smw:hasCrimeCategory ?crimeCategory .
      ?crimeCategory rdfs:label ?crimeCategoryName ;
                     smw:hasFrequency ?frequency .

      # Dynamic year filter
      FILTER({year_filter})

      FILTER(BOUND(?countyName) && BOUND(?fipsCode))
    }}
    GROUP BY ?countyName ?fipsCode
    ORDER BY ?fipsCode
    """

    try:
        print("Constructed SPARQL Query:\n", sparql_query)
        raw_results = query_sparql(sparql_query)

        if not raw_results.get("results") or not raw_results["results"].get("bindings"):
            print("No results or invalid response structure")
            return jsonify({"error": "No results match your query. Please adjust the filters."}), 404

        processed_data = []
        
        for result in raw_results["results"]["bindings"]:
            fips_code = result.get("fipsCode", {}).get("value", "N/A")
            
            if len(fips_code) == 4:
                fips_code = f"0{fips_code}"

            frequencies = result.get("frequencies", {}).get("value", "")
            
            frequency_list = frequencies.split(", ") if frequencies else []
            total_frequency = 0
            for frequency in frequency_list:
                frequency_value = frequency.split("_")[-1]
                try:
                    total_frequency += int(frequency_value)
                except ValueError:
                    pass

            processed_data.append({
                "id": fips_code,
                "value": total_frequency
            })

        return jsonify(processed_data)

    except Exception as e:
        print("Error executing SPARQL query:", str(e))
        return jsonify({"error": str(e)}), 500
