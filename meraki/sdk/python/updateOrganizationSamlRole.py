import meraki

# Defining your API key as a variable in source code is not recommended
API_KEY = '6bec40cf957de430a6f1f2baa056b99a4fac9ea0'
# Instead, use an environment variable as shown under the Usage section
# @ https://github.com/meraki/dashboard-api-python/

dashboard = meraki.DashboardAPI(API_KEY)

organization_id = '549236'
saml_role_id = ''

response = dashboard.organizations.updateOrganizationSamlRole(
    organization_id, saml_role_id, 
    role='myrole', 
    orgAccess='none', 
    tags=[{'tag': 'west', 'access': 'read-only'}], 
    networks=[{'id': 'N_24329156', 'access': 'full'}]
)

print(response)