import os


class Config:
    DATABASE_PATH = os.getenv(
        "DATABASE_PATH",
        os.path.join("data", "resources.db"),
    )
