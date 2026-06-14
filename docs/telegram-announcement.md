# Telegram Announcement Draft

hey frens, I cleaned up and open-sourced a sanitized version of my Stormforge
setup.

Repo:
https://github.com/welttowelt/stormforge-ecdsa-harness

Demo dashboard:
https://welttowelt.github.io/stormforge-ecdsa-harness/

Important framing: this is not the original ecdsa.fail harness. The base
challenge/platform comes from Gautham / ecdsa.fail. Gajesh also shared many
useful setup ideas around custom agents, goal mode, workflows, and more
agent-readable code.

My repo is the extra operator layer I built around it: mailbox coordination,
ACK/read receipts, worker roles, route packets, validation gates, dashboard
views, redaction checks, and credit discipline.

It is fixture/demo only: no private logs, no endpoints, no nonces, no live
routes.

Credits are a big part of it because many good ideas came from this group:
Gautham, Gajesh, BitWonka, nasqret/Bartosz, Jieyi, Frosty/newjordan, Teddy, Sam,
zuiris/Maksim, gnuchev, and everyone sharing notes.

Would love feedback, especially if I missed a credit or should sanitize
something harder.
