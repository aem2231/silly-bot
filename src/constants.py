from pathlib import Path

DB_PATH = Path("db1/database.db")
USER_TABLE = "users"
GUILD_TABLE = "server"
USER_COLUMN = "user_id"
GUILD_COLUMN = "guild_id"
DAILY_COLUMN = "last_daily"
BANK_ROB_COLUMN = "last_bank_rob"
WORK_COLUMN = "last_work"

DAILY_PAYOUT = 1000
MIN_BANK_ROB_PAYOUT = 1000
MAX_BANK_ROB_PAYOUT = 5000
MIN_BEG_PAYOUT=5
MAX_BEG_PAYOUT=50
MIN_WORK_PAYOUT = 250
MAX_WORK_PAYOUT = 1500

COOLDOWNS = {
    "bank_rob": 1800,
    "work": 21600,
    "daily": 86400,
}

JOB_LIST = [
    "cleaner",
    "cashier",
    "uber driver",
    "bartender",
    "binman",
    "twitch streamer",
    "delivery driver",
    "bus driver",
]
