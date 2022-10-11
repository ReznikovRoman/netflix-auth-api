User roles
===============================

Context
------
- User has a list of roles (`viewer`, `subscriber`, etc.).
- If user has some specific roles, he gets access to extended platform's functionality .
- There is already an API for checking user roles.
- Roles are often checked in services, so we would like to speed up this process.

Decision
------
User roles are stored in a JWT claim `additional claims`.

Any client can decode the token using a secret key and get a list of roles.

Consequences
------
If the user roles are updated (e.g., he purchases a subscription and retrieves `subscriber` role),
and the client continues to use the old access token,
then we will define user roles incorrectly (because roles have not been changed in the old access token).

We assume that clients themselves would be responsible for the correct and timely token updates.
(e.g., retrieving a new access token after changing roles using the refresh token).
And the services that need role verification will not be responsible for that.
