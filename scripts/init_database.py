from app.infrastructure.database import engine
from app.infrastructure.models import Base


def main():

    print("Creating database tables...")

    Base.metadata.create_all(
        bind=engine
    )

    print("Database tables created.")


if __name__ == "__main__":
    main()