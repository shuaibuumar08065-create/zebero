from flask import (
    render_template,
    request,
    redirect,
)

from models import (
    create_task,
    get_all_tasks,
    delete_task,
)


def admin_tasks():

    if request.method == "POST":

        title = request.form["title"].strip()

        description = request.form["description"].strip()

        reward = float(request.form["reward"])

        task_url = request.form["task_url"].strip()

        task_type = request.form["task_type"]

        upgrade_level = request.form.get(
            "upgrade_level",
            "",
        )

        if task_type == "normal":

            upgrade_level = ""

        elif upgrade_level == "":

            return "Please select upgrade level."

        create_task(
            title,
            description,
            reward,
            task_url,
            task_type,
            upgrade_level,
        )

        return redirect("/admin/tasks")

    tasks = get_all_tasks()

    tasks = [dict(task) for task in tasks]

    for task in tasks:

        if task["task_type"] == "normal":

            task["type_name"] = "Normal"

            task["level_name"] = "-"

        else:

            task["type_name"] = "Upgrade"

            task["level_name"] = (
                task["upgrade_level"].capitalize()
            )

    return render_template(
        "admin/tasks.html",
        tasks=tasks,
    )


def admin_delete_task(task_id):

    delete_task(task_id)

    return redirect("/admin/tasks")
