from flask import Blueprint, request, jsonify
from utils.sparql_helper import query_sparql

# Define Blueprint for Use Case 3
use_case_3_bp = Blueprint("use_case_3", __name__)

@use_case_3_bp.route("/use-case-3", methods=["POST"])
def use_case_3():
    # Extract user inputs from the request
    data = request.json
    selected_state = data.get("selectedState", "")  # Mandatory state selection
    selected_county = data.get("selectedCounty", "")  # Optional county selection

    # Define the mapping from crime category code to human-readable name
    crime_name_mapping = {
        "AGASSLT": "Aggravated Assault",
        "DUI": "DUI",
        "FRAUD": "Fraud",
        "MURDER": "Murder",
        "RAPE": "Rape",
        "ROBBERY": "Robbery",
        "WEAPONS": "Weapons"
    }

    # Construct the SPARQL query with the selected state and county
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
      FILTER(CONTAINS(STR(?crimeYear), "2013"))
      
      ?crimeYear smw:hasCrimeCategory ?crimeCategory .
      ?crimeCategory rdfs:label ?crimeCategoryName ;
                     smw:hasFrequency ?frequency .
    }}
    ORDER BY ?crimeCategoryName
    """

    try:
        # Execute SPARQL query and log it
        print("Constructed SPARQL Query:\n", sparql_query)
        raw_results = query_sparql(sparql_query)

        if not raw_results.get("results") or not raw_results["results"].get("bindings"):
            print("No results or invalid response structure")
            return jsonify({"error": "No results match your query. Please adjust the filters."}), 404

        # Create the result list with headers
        processed_data = [['Crime Name', 'Number of crimes']]

        # Process the results and map them to the desired format
        for result in raw_results["results"]["bindings"]:
            crime_code = result.get("crimeCategoryName", {}).get("value", "")
            frequency = result.get("frequency", {}).get("value", "")

            # Extract the number of crimes from the frequency field
            try:
                num_crimes = int(frequency.split('_')[-1])  # Extract the last part as the number of crimes

                # Get the human-readable crime name from the mapping
                crime_name = crime_name_mapping.get(crime_code, crime_code)  # Default to the code if not found

                # Add the entry to the result list
                processed_data.append([crime_name, num_crimes])
            except ValueError:
                # Handle the case where the frequency doesn't have a valid number
                print(f"Error processing frequency for {crime_code}: {frequency}")

        # Return the processed data
        return jsonify({"results": processed_data})

    except Exception as e:
        print("Error executing SPARQL query:", str(e))
        return jsonify({"error": str(e)}), 500
