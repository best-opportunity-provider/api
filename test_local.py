import json

from config import *
from scripts.country_load import update_countries

update_countries()

# with open('OpportunityMainInfo.json', 'w') as f:
#     f.write(json.dumps(opportunity.opportunity_partial.OpportunityMainInfo.model_json_schema()))

# with open('OpportunityDetailsInfo.json', 'w') as f:
#     f.write(json.dumps(opportunity.opportunity_partial.OpportunityDetailsInfo.model_json_schema()))

# with open('OpportunitySelectionInfo.json', 'w') as f:
#     f.write(json.dumps(opportunity.opportunity_partial.OpportunitySelectionInfo.model_json_schema()))

# with open('OpportunityGeoInfo.json', 'w') as f:
#     f.write(json.dumps(opportunity.opportunity_partial.OpportunityGeoInfo.model_json_schema))

# with open('OpportunityTagsInfo.json', 'w') as f:
#     f.write(json.dumps(opportunity.opportunity_partial.OpportunityTagsInfo.model_json_schema()))

# with open('OpportunityFormInfo.json', 'w') as f:
#     f.write(json.dumps(opportunity.opportunity_partial.OpportunityFormInfo.model_json_schema()))
