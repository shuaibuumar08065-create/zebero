import os

from flask import (
    render_template,
    request,
    redirect,
    session,
)

from werkzeug.utils import secure_filename

from models import get_task

from verification.models import (
    create_verification,
    has_verification,
)

UPLOAD_FOLDER = "static/uploads/tasks"


def verification_page(task_id):

    if "user" not in session:
        return redirect("/login")

    task = get_task(task_id)

    if not task:
        return "Task not found."

    verification = has_verification(
        session["user"]["id"],
        task_id,
    )

    return render_template(
        "verification/index.html",
        task=task,
        verification=verification,
    )


def submit_verification(task_id):

    if "user" not in session:
        return redirect("/login")

    task = get_task(task_id)

    if not task:
        return redirect("/earn")

    user_id = session["user"]["id"]

    if has_verification(user_id, task_id):
        return redirect("/verification/" + str(task_id))

    if "screenshot" not in request.files:
        return redirect("/verification/" + str(task_id))

    screenshot = request.files["screenshot"]

    if screenshot.filename == "":
        return redirect("/verification/" + str(task_id))

    os.makedirs(
        UPLOAD_FOLDER,
        exist_ok=True,
    )

    filename = secure_filename(screenshot.filename)

    filepath = os.path.join(
        UPLOAD_FOLDER,
        filename,
    )

    screenshot.save(filepath)

    create_verification(
        user_id,
        task_id,
        filename,
    )

    return redirect("/earn")
