"""
Shared household-access helpers used across multiple route modules.

Role hierarchy (highest → lowest):
    owner  4  — full control; assigned on household creation
    admin  3  — can kick member/restricted, edit+delete recipes
    member 2  — can edit recipes
    restricted 1  — view only
"""
from flask import g

from db.session import get_db

ROLE_RANK: dict[str, int] = {
    "owner":      4,
    "admin":      3,
    "member":     2,
    "restricted": 1,
}


def get_member_role(household_id: int) -> str | None:
    """Return the current user's role in the household, or None if not a member."""
    row = get_db().execute(
        "SELECT role FROM household_members WHERE household_id = ? AND user_id = ?",
        (household_id, g.current_user["id"]),
    ).fetchone()
    return row["role"] if row else None


def has_access(household_id: int) -> bool:
    """True if the current user is a member of the given household."""
    return get_member_role(household_id) is not None


def is_hh_admin(household_id: int) -> bool:
    """True if the current user is owner or admin of the household."""
    return ROLE_RANK.get(get_member_role(household_id) or "", 0) >= ROLE_RANK["admin"]


def is_hh_owner(household_id: int) -> bool:
    """True if the current user is the owner of the household."""
    return get_member_role(household_id) == "owner"


def can_view_recipe(recipe_id) -> bool:
    """
    True if the current user may see this recipe.

    Mirrors the rule enforced by GET /api/recipes/<id>: public recipes are
    visible to everyone, private ones only to members of their household.
    Anything that stores a caller-supplied recipe_id must check this, or the
    recipe's name and description leak back out through a JOIN.
    """
    row = get_db().execute(
        "SELECT household_id, is_public FROM recipes WHERE id = ?", (recipe_id,)
    ).fetchone()
    if not row:
        return False
    # NULL is_public counts as public — same coercion as db.models.recipe_dict
    if row["is_public"] is None or row["is_public"] != 0:
        return True
    return has_access(row["household_id"])


def location_in_household(location_id, household_id) -> bool:
    """True if this storage location belongs to the given household."""
    row = get_db().execute(
        "SELECT 1 FROM storage_locations WHERE id = ? AND household_id = ?",
        (location_id, household_id),
    ).fetchone()
    return row is not None
