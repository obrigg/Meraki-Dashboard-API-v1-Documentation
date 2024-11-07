# OAuth 2.0

## OAuth 2.0 Overview

Meraki APIs are RESTful APIs customers and partners can use to programmatically manage and monitor Meraki environments. Until now, API access was only possible via user-scoped API keys, and today Meraki is introducing a new application-scoped auth method based on OAuth 2.0. In most cases, this new OAuth method can replace an application’s reliance on the user-scoped API keys, which have driven application integrations so far, to realize many benefits not available to user-scoped API keys.

## What is OAuth 2.0?

OAuth 2.0 is a standard authorization framework that enables integrations to access Meraki data without users revealing their credentials/API keys. OAuth 2.0 is widely used for delegated access, particularly in the context of APIs and web applications, providing a secure and standardized way for users to authorize third-party access to their resources while maintaining control over their data.

Learn more about the OAuth framework and definitions: [https://oauth.net/2/](https://oauth.net/2/)

## Benefits of OAuth 2.0 integrations

OAuth 2.0 offers several benefits over traditional API keys:

1. **Flexible and least-privilege access compared to user-scoped API keys**: With OAuth 2.0, developers may request permission to a limited set of OAuth scopes, instead of an all-or-nothing access level.
2. **No more copying and pasting API keys**: OAuth 2.0 introduces a secure and seamless grant flow for Meraki and the integration to exchange credentials.
3. **No more API key rotations**: OAuth 2.0 introduces short-lived access tokens that will automatically be replaced in a matter of minutes, not months or years.
4. **Simplifying auditing**: With OAuth 2.0, every integration has its own identity - each API call can be easily traced back to the integration invoking it.

## Building an OAuth 2.0 integration

To build an OAuth 2.0 integration, follow these steps:
1. Register your integration with Meraki.
2. Request permission using an OAuth Grant Flow from an organization admin for the organization you’d like to manage.
3. Use the Access Token to make API calls.
4. Refresh your Access Token using your Refresh Token as necessary.


### 1. Register your integration with Meraki

1. Access the application registry: [integrate.cisco.com](https://integrate.cisco.com), using your cisco.com credentials to log in. 
2. Create a new app, provide the name, redirect URIs, select the relevant scopes, etc. 

Note that the `client_secret` will be shown only once. **Make sure you save the `client_secret` securely**. Scopes and redirect URIs can be edited later.

### 2. Request permission using an OAuth grant flow

#### Obtaining an access_token and refresh_token:

1. Create a “Connect to Meraki” button or link in your application that will initiate the OAuth process.

- The Meraki admin should be redirected to [https://as.meraki.com/oauth/authorize](https://as.meraki.com/oauth/authorize), with the following required query parameters:

  - `response_type`: Must be set as `code`
  - `client_id`: Issued when creating your app
  - `redirect_uri`: Must match one of the URIs provided during integration registration
  - `scope`: A space-separated list of scopes being requested by your integration (see scopes)
  - `state`: A unique string that will be passed back to your integration upon completion.
  - `nonce` (optional)

The link should have the following format:
https://as.meraki.com/oauth/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_url}&scope={scopes}

2. Implement a callback receiver on your application that will respond when a request gets back to the redirection URL. You should expect to receive a `code` attribute as one of the request parameters - that is the access grant, and it has a lifetime of 10 minutes.

3. Use the access grant to request a refresh token and an access token.

- You will need to send a POST request to [https://as.meraki.com/oauth/token](https://as.meraki.com/oauth/token)
- The headers will include “application/x-www-form-urlencoded” as the “Content-Type”.
- Authentication should be set for basic authentication, using the `client_id` and `client_secret`
- The payload will include:
    ```json
    {
    'grant_type': 'authorization_code',
    'code': {the access code received in the callback},
    'redirect_uri': {redirect_url},
    'scope': {scopes}
    }
    ```
- The response will include the `access_token` (available for 60 minutes) and the `refresh_token` which will be used to generate new `access_token`s.
- You are **REQUIRED** to securely store the refresh token.

### 3. Use the OAuth access token to make your API calls
Congratulations! You can now make API calls to api.meraki.com using the `access_token`. The API calls will use the `Authorization` header with `Bearer + access_token` similar to how API calls were made with API keys. If you were previously using an API key for your application, then for most, if not all operations, you can simply swap in your OAuth access token in place of the API key.

### 4. Refresh your OAuth access token using your OAuth refresh token
Based on: https://datatracker.ietf.org/doc/html/rfc6749#section-6 

1. While an access_token will expire 60 minutes after being generated, the refresh_token is long-lived and will be used to obtain a new access_tokens.
Send a POST request to https://as.meraki.com/oauth/token
The client MUST authenticate according to https://datatracker.ietf.org/doc/html/rfc6749#section-2.3.1. **It is STRONGLY RECOMMENDED using HTTP Basic authentication**.

2. The headers must include:
`Content-Type: application/x-www-form-urlencoded`
3. The payload must include: 
`grant_type=refresh_token&refresh_token={refresh_token}`
4. The response will include a new `refresh_token` and a new `access_token` (available for 60 minutes).
5. Once the new `refresh_token` or `access_token` are used, the previous `refresh_token` will be revoked for security hygiene. Ensure you securely store the new tokens.

**Note: The refresh_token will be revoked automatically after 90 days of inactivity**.

### 5. Revoking OAuth refresh tokens
A refresh token can be revoked by the Dashboard admin (resource owner) or by the 3rd party application (client application).
1. Dashboard admin revocation:
The Dashboard admin can browse to “organization” > “integrations” > “my integrations”, select the relevant integration, and choose “remove”.
Currently, the client application will not be notified when its token has been revoked - API calls using the access token and refresh token will fail.

2. Client application revocation:
You can revoke the refresh token from the client application, per https://datatracker.ietf.org/doc/html/rfc7009.
- You will need to send a POST request to https://as.meraki.com/oauth/revoke
- The headers will include `application/x-www-form-urlencoded` as the `Content-Type`.
- `Authentication` should be set for basic authentication, using the `client_id` and `client_secret`
- The payload will include: 
```
{'token': <the refresh token to be revoked>,
  'token_type_hint': ‘refresh_token}
```
Expect a `200 OK` response.

**Note: It may take up to 10 minutes for the revoked access token to stop working**.

## Troubleshooting

### Supported clusters
OAuth is currently supported only on Meraki.com. Support for FedRAMP, China, Canada, and India will be added in a future phase.

### Initial grant flow
1. The user can’t find the relevant organization in the dropdown menu.
For an organization to appear in the dropdown menu, the following conditions must be met:
- The user has full organization admin rights - read-only and/or network admins will not see their organization.
- The app hasn’t been integrated already - if it has, the user must revoke its access under “organization” > “integrations” > “my integrations” and try again.

2. "An error has occurred: The requested redirect uri is malformed or doesn't match the client redirect URI".
- The redirect URI in the request is different from the redirect URIs registered in the app registry.
3. "An error has occurred: Client authentication failed due to unknown client, no client authentication included, or unsupported authentication method.."
- The client ID in the request is wrong.

### Errors returned to the redirect URI
(redirect URI being https://localhost/ for the following examples):
1. https://localhost?error=invalid_scope&error_description=The+requested+scope+is+invalid%2C+unknown%2C+or+malformed.
- There is either a mistake in one of the scopes, or the request includes scopes that are not included in the app registration.

2. https://localhost?error=access_denied&error_description=The+resource+owner+or+authorization+server+denied+the+request.
- The user denied access.

### Errors exchanging tokens
1. The provided authorization grant is invalid, expired, revoked, does not match the redirection URI used in the authorization request, or was issued to another client.
- The access grant may have been used already.
- More than 10 minutes have passed since the access grant was generated.
- The access grant does ot 

## Understanding OAuth scopes
OAuth scopes are a mechanism used in OAuth 2.0 to define and limit the access rights granted to an access token. When an integration requests authorization from the Meraki admin, it includes a list of scopes that it wants access to. The Meraki Dashboard then presents these scopes to the Meraki admin during the authorization process, allowing them to approve or deny the request.
By using scopes, OAuth 2.0 provides a flexible and granular approach to controlling access to resources, allowing Meraki admins to make informed decisions about the level of access they grant to integrations. Additionally, scopes help ensure that integrations are provisioned access by the principle of least privilege, enhancing security and privacy.

Meraki offers two types of scopes - `config` scopes and `telemetry` scopes. Each scope has two permission levels: “read-only” and “write”.

1. **`Config`** scopes grant access to configuration features that determine the operation of the network and the network experience. These features typically dictate the end-user network experience and the operation of Meraki devices, e.g. VPNs, VLANs, access controls, policies, SSIDs, and sensor names. Importantly, this excludes admin-facing telemetry configs, which can be managed via the next type of scope.
2. **`Telemetry`** scopes grant access to telemetry and telemetry configuration that does not affect the end-user experience of the network. For example, features like event log, syslog, bandwidth utilization, client count, and camera snapshots.

| Category              | Read                           | Write                          |
|-----------------------|--------------------------------|--------------------------------|
| **Dashboard**         | dashboard:iam:config:read     | dashboard:iam:config:write     |
|                       | dashboard:iam:telemetry:read  | dashboard:iam:telemetry:write  |
|                       | dashboard:general:config:read | dashboard:general:config:write |
|                       | dashboard:general:telemetry:read | dashboard:general:telemetry:write |
|                       | dashboard:licensing:config:read | dashboard:licensing:config:write |
|                       | dashboard:licensing:telemetry:read | dashboard:licensing:telemetry:write |
| **Network**           | sdwan:config:read             | sdwan:config:write             |
|                       | switch:config:read            | switch:config:write            |
|                       | wireless:config:read          | wireless:config:write          |
|                       | sdwan:telemetry:read          | sdwan:telemetry:write          |
|                       | switch:telemetry:read         | switch:telemetry:write         |
|                       | wireless:telemetry:read       | wireless:telemetry:write       |
| **IoT**               | camera:config:read            | camera:config:write            |
|                       | sensor:config:read            | sensor:config:write            |
|                       | camera:telemetry:read         | camera:telemetry:write         |
|                       | sensor:telemetry:read         | sensor:telemetry:write         |
| **Endpoint Management (SM)** | sm:telemetry:read      | sm:telemetry:write             |
|                       | sm:config:read                | sm:config:write                |

