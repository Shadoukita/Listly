"""
Invite-link validity rules, shared by the check / register / list routes.

Invites are single-use and time-limited. Rows created before expires_at existed
have NULL there; those fall back to created_at + INVITE_TTL_DAYS rather than
being treated as valid forever.
"""
INVITE_TTL_DAYS = 7

# Reusable SQL predicate — an invite is redeemable when it is unused and the
# effective expiry is still in the future. Both timestamps are UTC.
VALID_INVITE_SQL = (
    "used = 0 AND datetime("
    f"COALESCE(expires_at, datetime(created_at, '+{INVITE_TTL_DAYS} days'))"
    ") > datetime('now')"
)
