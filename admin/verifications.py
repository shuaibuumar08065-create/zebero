from flask import (
    render_template,
    redirect,
)

from verification.models import (
    get_all_verifications,
)
from verification.models import (
    get_verification,
    update_verification_status,
    add_balance,
)


def admin_verifications():

    verifications = get_all_verifications()

    return render_template(
        "admin/verifications.html",
        verifications=verifications,
    )


def approve_verification(verification_id):

    verification = get_verification(
        verification_id,
    )

    if not verification:
        return redirect("/admin/verifications")

    if verification["status"] == "approved":
        return redirect("/admin/verifications")

    add_balance(
        verification["user_id"],
        verification["reward"],
    )

    update_verification_status(
        verification_id,
        "approved",
    )

    return redirect("/admin/verifications")
def reject_verification(verification_id):

    verification = get_verification(
        verification_id,
    )

    if not verification:
        return redirect("/admin/verifications")

    update_verification_status(
        verification_id,
        "rejected",
    )

    return redirect("/admin/verifications")
