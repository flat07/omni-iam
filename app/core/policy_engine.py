from app.core.security import utc_now

from sqlalchemy.orm import Session
from app.models.policy import Policy
def evaluate_policy(policy, user, resource):

    conditions = policy.conditions or {}

    if conditions.get("department_match"):
        if resource.department_id != user.department_id:
            return False

    if conditions.get("location_match"):
        if resource.location_id != user.location_id:
            return False

    if "allowed_hours" in conditions:
        hour = utc_now().hour

        if hour not in conditions["allowed_hours"]:
            return False

    return True


def check_policy(
    db: Session,
    vendor_id: str,
    action: str,
    resource: str,
    context: dict
):

    policies = (
        db.query(Policy)
        .filter(
            Policy.vendor_id == vendor_id,
            Policy.enabled == True,
            Policy.action == action,
            Policy.resource == resource
        )
        .all()
    )

    for policy in policies:

        if not policy.conditions:
            if policy.effect == "allow":
                return True

        matched = True

        for key, value in policy.conditions.items():

            if context.get(key) != value:
                matched = False
                break

        if matched:

            if policy.effect == "deny":
                return False

            if policy.effect == "allow":
                return True

    return False