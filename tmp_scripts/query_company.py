import sys
from pathlib import Path
import json

# Adjust sys.path to import from ai_tender_system
# Assuming the current working directory is /Users/lvhe/Downloads/zhongbiao/zhongbiao/
# The ai_tender_system module is at /Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system
sys.path.insert(0, str(Path(__file__).parent.parent / 'ai_tender_system'))

from common.database import get_knowledge_base_db

db = get_knowledge_base_db()
companies = db.get_companies()

target_company_name = "智慧足迹数据科技有限公司"
company_info = None
for company in companies:
    if company['company_name'] == target_company_name:
        company_info = company
        break

if company_info:
    full_company_details = db.get_company_by_id(company_info['company_id'])
    if full_company_details:
        # Convert Row object to dict for JSON serialization
        details_dict = dict(full_company_details)
        print(json.dumps(details_dict, ensure_ascii=False, indent=2))
    else:
        print(f"Could not retrieve full details for company ID: {company_info['company_id']}")
else:
    print(f"Company '{target_company_name}' not found.")
