import meraki

# Defining your API key as a variable in source code is discouraged.
# This API key is for a read-only docs-specific environment.
# In your own code, use an environment variable as shown under the Usage section
# @ https://github.com/meraki/dashboard-api-python/

API_KEY = '75dd5334bef4d2bc96f26138c163c0a3fa0b5ca6'

dashboard = meraki.DashboardAPI(API_KEY)

network_id = 'L_646829496481105433'
rule_id = ''

response = dashboard.wireless.updateNetworkWirelessAirMarshalRule(
    network_id, rule_id, 
    type='allow', 
    match={'type': 'bssid', 'string': '00:11:22:33:44:55'}
)

print(response)