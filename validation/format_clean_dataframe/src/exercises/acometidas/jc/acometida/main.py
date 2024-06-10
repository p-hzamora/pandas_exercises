
from pathlib import Path
from code import Tasks


if __name__ == "__main__":

    file =  Path(__file__).parent.parent.parent.parent.parent.parent / "test" / "data_acometida.csv"

    tfd = Tasks(file)

    (
        tfd.load_data()
            .replace_values()
            .replace_headers()
            .add_blank_rows(2)
            .add_observation_row()
    )

    print(tfd.df)
