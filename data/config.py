from environs import Env

env = Env()
env.read_env()

BOT_TOKEN: str = env.str("BOT_TOKEN")
DB_NAME: str = env.str("DB_NAME")
ADMINS_ID = env.list("ADMINS_ID")
