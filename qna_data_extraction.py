# qna_data_extraction.py
def extract_fund_insights(data):
    """
    Extrait les informations clés à partir des données fournies (par exemple, performance, conformité).
    
    Args:
        data (dict): Données extraites via le système Q&A.
        
    Returns:
        dict: Insights extraits, comme la performance, les métriques de conformité, etc.
    """
    fund_performance = data.get("performance", {})
    compliance_metrics = data.get("compliance", {})
    
    insights = {
        "performance": fund_performance,
        "compliance": compliance_metrics,
        "key_metrics": {
            "asset_size": data.get("asset_size", 0),
            "risk_score": data.get("risk_score", 0),
            "latest_report_date": data.get("latest_report_date", "N/A")
        }
    }
    
    return insights
