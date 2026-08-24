from typing import Dict, Any


KNOWN_ALIASES = {
    "TCS Ltd": "Tata Consultancy Services",
    "Tata Sons - TCS Div": "Tata Consultancy Services",
    "T.C.S. IND": "Tata Consultancy Services",
    "Reliance Ind - Retail": "Reliance Retail Ltd",
    "R-Retail Ventures": "Reliance Retail Ltd",
    "RELIANCE RETAIL": "Reliance Retail Ltd",
    "Infosys Ltd": "Infosys Technologies",
    "INFOSYS TECH": "Infosys Technologies",
    "Infy Software Div": "Infosys Technologies",
    "Zomato Ltd": "Zomato Media Pvt Ltd",
    "ZOMATO HYPERPURE": "Zomato Media Pvt Ltd",
    "Zomato Online": "Zomato Media Pvt Ltd",
    "Bundl Tech Swiggy": "Swiggy Bundl Technologies",
    "SWIGGY BANGALORE": "Swiggy Bundl Technologies",
    "Swiggy Delivery": "Swiggy Bundl Technologies",
    "Flipkart India": "Flipkart Internet Pvt Ltd",
    "FLIPKART PAYMENTS": "Flipkart Internet Pvt Ltd",
    "FK Internet": "Flipkart Internet Pvt Ltd",
    "Zerodha Securities": "Zerodha Broking Ltd",
    "ZERODHA BROKING": "Zerodha Broking Ltd",
    "Zerodha Trading": "Zerodha Broking Ltd",
}


def match_customer_entity(customer_name: str, bank_description: str) -> Dict[str, Any]:
    """
    Checks if a bank statement description references a verified alias of the registered customer name.
    """
    if not bank_description:
        return {"matched": False, "reason": "Empty bank description"}

    # Exact direct string containment
    if customer_name.lower() in bank_description.lower():
        return {
            "matched": True,
            "confidence": 0.99,
            "matched_name": customer_name,
            "evidence": f"Bank description directly mentions '{customer_name}'.",
        }

    # Alias table lookup
    for alias, canonical in KNOWN_ALIASES.items():
        if canonical == customer_name and alias.lower() in bank_description.lower():
            return {
                "matched": True,
                "confidence": 0.96,
                "matched_name": alias,
                "canonical_name": canonical,
                "evidence": f"Bank description references alias '{alias}' for canonical entity '{canonical}'.",
            }

    return {
        "matched": False,
        "confidence": 0.30,
        "reason": f"No entity alias matched between '{customer_name}' and '{bank_description}'.",
    }