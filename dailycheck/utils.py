from datetime import date, timedelta

from dailycheck.models import (
    get_daily_record,
    create_daily_record,
    get_reward,
    connect,
)


def claim_daily_reward(user_id):
    create_daily_record(user_id)

    record = get_daily_record(user_id)

    today = date.today()

    if record["last_claim_date"]:

        last_date = date.fromisoformat(
            record["last_claim_date"]
        )

        # Already claimed today
        if last_date == today:
            return {
                "success": False,
                "message": "You already claimed today's reward."
            }

        # Missed a day -> reset to Day 1
        if (today - last_date) > timedelta(days=1):

            day = 1

        else:

            day = record["current_day"] + 1

            if day > 7:
                day = 1

    else:

        day = 1

    reward = get_reward(day)

    conn = connect()

    conn.execute(
        """
        UPDATE daily_rewards
        SET
            current_day=?,
            last_claim_date=?
        WHERE user_id=?
        """,
        (
            day,
            today.isoformat(),
            user_id,
        ),
    )

    conn.execute(
        """
        UPDATE users
        SET balance =
            COALESCE(balance,0)+?
        WHERE id=?
        """,
        (
            reward,
            user_id,
        ),
    )

    conn.commit()
    conn.close()

    return {
        "success": True,
        "day": day,
        "reward": reward,
    }
