import meraki

# Defining your API key as a variable in source code is not recommended
API_KEY = '6bec40cf957de430a6f1f2baa056b99a4fac9ea0'
# Instead, use an environment variable as shown under the Usage section
# @ https://github.com/meraki/dashboard-api-python/

dashboard = meraki.DashboardAPI(API_KEY)

organization_id = '549236'

response = dashboard.organizations.updateOrganizationSnmp(
    organization_id, 
    v2cEnabled=False, 
    v3Enabled=True, 
    v3AuthMode='SHA', 
    v3PrivMode='AES128', 
    peerIps='123.123.123.1'
)

print(response)