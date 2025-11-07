import requests
import re

WIKIDATA_SPARQL_URL = "https://query.wikidata.org/sparql"
HEADERS = {"Accept": "application/sparql-results+json"}

def extract_company_sector(company_name):
    """
    Dato il nome di un'azienda, cerca il suo settore/industry su Wikidata
    usando la API di EntitySearch.
    Restituisce una lista di industrie trovate.
    """
    # Costruisci la query SPARQL dinamicamente
    sparql = f"""
    SELECT ?company ?companyLabel ?industry ?industryLabel WHERE {{
      SERVICE wikibase:mwapi {{
        bd:serviceParam wikibase:endpoint "www.wikidata.org";
                        wikibase:api "EntitySearch";
                        mwapi:search "{company_name}";
                        mwapi:language "en".
        ?company wikibase:apiOutputItem mwapi:item .
      }}
      OPTIONAL {{ ?company wdt:P452 ?industry . }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
    }}
    LIMIT 10
    """

    try:
        resp = requests.get(WIKIDATA_SPARQL_URL, params={"query": sparql}, headers=HEADERS)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"⚠️ Errore durante la query Wikidata: {e}")
        return None

    # Estrai le industrie
    industries = []
    for binding in data.get("results", {}).get("bindings", []):
        val = binding.get("industryLabel", {}).get("value", "")
        # Aggiungi solo se NON è un Qnumber (es. "Q12345")
        if val and not re.fullmatch(r"Q\d+", val):
            industries.append(val)

    # Rimuove duplicati
    return list(set(industries))

'''
# --- Esempio di utilizzo ---
if __name__ == "__main__":
    company = "Eni"
    sectors = extract_company_sector(company)
    print(f"{company} : {', '.join(sectors) if sectors else 'Nessun settore trovato'}")
'''
