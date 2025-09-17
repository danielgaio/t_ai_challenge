import pandas as pd
from .package_dispatcher import sort

class DispatcherFlow:
    def __init__(self):
        self.input_data = None
        # save statistics here
        self.statistics = {
            "total_number_of_packages": 0,
            "average_mass": 0.0,
            "max_mass": 0.0,
            "min_mass": 0.0,
            "average_volume": 0.0,
            "max_volume": 0.0,
            "min_volume": 0.0,
        }

        # staks, number of packages in each stack, and percentage of items in each stack
        # STANDARD
        # ESPECIAL
        # REJECTED

    def load_data(self, file_path):
        """Load data from a CSV file."""
        try:
            # self.input_data = pd.read_csv(file_path)
            self.input_data = pd.read_csv(
                file_path,
                on_bad_lines="skip",        # "skip", "warn", or a callable
                engine="python",            # more tolerant parser for messy files
                na_values=["None", ""],     # treat case 'None' and blanks as NA
                keep_default_na=False,      # optionally disable pandas' default NAs
                skip_blank_lines=True
            )
            # remore non-numeric values in specific columns
            for col in ["Width","Height","Length","Mass"]:
                self.input_data[col] = pd.to_numeric(self.input_data[col], errors="coerce")  # invalid -> NaN
            # drop rows where all elements are NaN
            self.input_data = self.input_data.dropna(how="any")            # drop rows with at least one NaN
            # example domain filter: keep only rows where Mass > 0
            self.input_data = self.input_data[self.input_data["Mass"] > 0]
            # remove rows with any negative values
            self.input_data = self.input_data[(self.input_data[["Width","Height","Length","Mass"]] >= 0).all(axis=1)]
            # debug print
            print(self.input_data)
            print("input data loaded successfully")
        except Exception as e:
            print(f"Error loading data: {e}")

    def run_sorting(self):
        """Run the sorting algorithm."""
        if self.input_data is None:
            print("No input data to process.")
            return
        
        # iterate over rows of input_dat calling the sort function
        for _, row in self.input_data.iterrows():
            width = row["Width"]
            height = row["Height"]
            length = row["Length"]
            mass = row["Mass"]
            stack = sort(width, height, length, mass)
            self.input_data.at[_, "Stack"] = stack  # add a new column "Stack" with the result
            print("Package with Width:", width, "Height:", height, "Length:", length, "Mass:", mass, "-> Stack:", stack)

        print("Sorting completed.")

    def show_statistics(self):
        """Calculate and display statistics."""
        if self.input_data is None or self.input_data.empty:
            print("No data available for statistics.")
            return
        
        self.statistics["total_number_of_packages"] = len(self.input_data)
        self.statistics["average_mass"] = round(self.input_data["Mass"].mean(), 2)
        self.statistics["max_mass"] = round(self.input_data["Mass"].max(), 2)
        self.statistics["min_mass"] = round(self.input_data["Mass"].min(), 2)
        volumes = self.input_data["Width"] * self.input_data["Height"] * self.input_data["Length"]
        self.statistics["average_volume"] = round(volumes.mean(), 2)
        self.statistics["max_volume"] = round(volumes.max(), 2)
        self.statistics["min_volume"] = round(volumes.min(), 2)

        print("\nStatistics:")
        for key, value in self.statistics.items():
            print(f"{key}: {value}")

        print("\nStack distribution:")
        print("\nPercentage of items in each stack:")
        print(round(self.input_data["Stack"].value_counts(normalize=True) * 100, 2))
        print("\nNumber of items in each stack:")
        print(self.input_data["Stack"].value_counts())
        print("Flow completed.")