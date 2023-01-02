import pandas as pd

from sqlalchemy import create_engine


def main():
    engine = create_engine("postgresql://root:root@pgdatabase3:5432/accidents")

    if engine.connect():
        print("connected succesfully")
    else:
        print("failed to connect")

    df = pd.read_csv("accidents_cleaned_milestone2.csv")
    df.to_sql(name="UK_Accidents_2011", con=engine, if_exists="replace")

    df = pd.read_csv("encodings.csv")
    df.to_sql(name="lookup_table", con=engine, if_exists="replace")


if __name__ == "__main__":
    main()
