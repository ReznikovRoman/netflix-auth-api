Temporary user password when logging in via a social network
===============================

Context
------
- Users can register via the social network.
- Each user must have a password.
- The `Netflix Notifications` service is currently not integrated.

Decision
------
At the current stage of the project, the same password is assigned for all users during social auth.

Consequences
------
**Major security issue**.
In the future, when registering via a social network, a random password will be generated and
sent to the user via email.
