#!/usr/bin/env python3
"""
Company Products Mapping for Multi-Product Sentiment Analysis
Structured data for all companies and their products with Capterra URLs
"""

COMPANY_PRODUCTS_MAPPING = {
    "Access Group": {
        "Access Recruitment CRM": "https://www.capterra.com/p/110208/RDB-Pronet/",
        "Access LMS Evo": "https://www.capterra.com/p/267473/Access-LMS/"
    },
    "Acumatica": {
        "Acumatica Cloud ERP": "https://www.capterra.com/p/96371/Acumatica-Cloud-ERP/reviews/"
    },
    "ADP": {
        "ADP Comprehensive Services": "https://www.capterra.com/p/175840/ADP-Comprehensive-Services/reviews/",
        "ADP Workforce Now": "https://www.capterra.com/p/155895/WorkforceNow/reviews/"
    },
    "BILL (Bill.com)": {
        "BILL Accounts Payable & Receivable": "https://www.capterra.com/p/166559/BILL/",
        "BILL Spend & Expense (formerly Divvy)": "https://www.capterra.com/p/166905/Divvy/"
    },
    "Microsoft": {
        "Dynamics 365": "https://www.capterra.com/p/138076/Microsoft-Dynamics-365/"
    },
    "Oracle NetSuite": {
        "NetSuite ERP": "https://www.capterra.com/p/80923/NetSuite/reviews/"
    },
    "SAP": {
        "SAP Business One": "https://www.capterra.com/p/66726/SAP-Business-One/reviews/"
    },
    "Sage": {
        "SageHR": "https://www.capterra.com/p/128705/SageHR/#reviews",
        "Sage 50cloud Accounting": "https://www.capterra.com/p/40636/Sage-50cloud-Accounting/reviews/",
        "Sage Intacct": "https://www.capterra.com/p/157901/Sage-Intacct/reviews/"
    },
    "Xero": {
        "Xero": "https://www.capterra.com/p/119802/Xero/reviews/"
    },
    "Workday": {
        "Workday HCM": "https://www.capterra.com/p/131066/Workday-HCM/reviews/"
    },
    "QuickBooks (Intuit)": {
        "QuickBooks Online": "https://www.capterra.com/p/124808/QuickBooks-Online/reviews/"
    },
    "Cegid": {
        "Cegid Talentsoft": "https://www.capterra.com/p/143682/Talentsoft/reviews/",
        "Cegid Retail": "https://www.capterra.com/p/134123/Cegid-Retail/reviews/"
    },
    "IRIS": {
        "IRIS Software": "https://www.capterra.com/p/111646/IRIS/reviews/"
    },
    "Jonas Construction": {
        "Jonas Enterprise": "https://www.capterra.com/p/116264/Jonas-Enterprise/reviews/"
    },
    "Emburse": {
        "Certify Expense": "https://www.capterra.com/p/128622/Certify/reviews/",
        "Emburse Chrome River": "https://www.capterra.com/p/114036/Chrome-River-EXPENSE/reviews/"
    },
    "Rippling": {
        "Rippling": "https://www.capterra.com/p/191937/Rippling/reviews/"
    },
    "Wolters Kluwer": {
        "CCH Tagetik": "https://www.capterra.com/p/117683/CCH-Tagetik/reviews/"
    },
    "Yooz": {
        "Yooz": "https://www.capterra.com/p/151837/Yooz/reviews/"
    },
    "SumUp": {
        "SumUp POS": "https://www.capterra.com/p/191986/SumUp/reviews/"
    },
    "Square (Block, Inc.)": {
        "Square Point of Sale": "https://www.capterra.com/p/140188/Square-Point-of-Sale/reviews/"
    },
    "Holded": {
        "Holded": "https://www.capterra.com/p/176098/Holded/reviews/"
    },
    "FastBill": {
        "FastBill": "https://www.capterra.com/p/122471/FastBill/reviews/"
    },
    "Bright Solutions Group": {
        "BrightPay": "https://www.capterra.com/p/152099/BrightPay/reviews/"
    },
    "BuchhaltungsButler": {
        "BuchhaltungsButler": "https://www.capterra.com/p/151408/BuchhaltungsButler/reviews/"
    },
    "Iplicit": {
        "iplicit": "https://www.capterra.com/p/198926/iplicit/reviews/"
    }
}

def get_companies():
    """Get list of all companies"""
    return list(COMPANY_PRODUCTS_MAPPING.keys())

def get_company_products(company_name: str):
    """Get products for a specific company"""
    return COMPANY_PRODUCTS_MAPPING.get(company_name, {})

def get_all_products():
    """Get all products across all companies"""
    all_products = {}
    for company, products in COMPANY_PRODUCTS_MAPPING.items():
        for product_name, url in products.items():
            all_products[f"{company} - {product_name}"] = {
                "company": company,
                "product": product_name,
                "url": url
            }
    return all_products

def get_companies_with_multiple_products():
    """Get companies that have multiple products"""
    return {
        company: products 
        for company, products in COMPANY_PRODUCTS_MAPPING.items() 
        if len(products) > 1
    }

# Example usage
if __name__ == "__main__":
    print("🏢 Companies with Multiple Products:")
    print("=" * 50)
    multi_product_companies = get_companies_with_multiple_products()
    for company, products in multi_product_companies.items():
        print(f"\n{company}:")
        for product_name, url in products.items():
            print(f"  - {product_name}: {url}")
    
    print(f"\n📊 Total Companies: {len(get_companies())}")
    print(f"📊 Companies with Multiple Products: {len(multi_product_companies)}") 