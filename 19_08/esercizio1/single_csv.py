import pandas as pd
import glob
import os

dataset_folder = "C:\\desktopnoonedrive\\Ai Academy\\deposito-addari-EY\\19_08\\esercizio1\\dataset"
output_folder = "C:\\desktopnoonedrive\\Ai Academy\\deposito-addari-EY\\19_08\\esercizio1\\csvs"

csv_files = glob.glob(os.path.join(dataset_folder, "*.csv"))

for file_path in csv_files:
	file_name = os.path.splitext(os.path.basename(file_path))[0]
	df = pd.read_csv(file_path)
	df['Datetime'] = pd.to_datetime(df['Datetime'])
	df.set_index('Datetime', inplace=True)

	daily_df = df.resample('D').mean()

	consumption_col = daily_df.columns[0]
	average_daily = daily_df[consumption_col].mean()
	daily_df['Consumption'] = daily_df[consumption_col].apply(lambda x: 'Alto' if x > average_daily else 'Basso')
	daily_out = os.path.join(output_folder, f"{file_name}_daily_high_low.csv")
	daily_df.to_csv(daily_out, index=True)

	weekly_df = df.resample('W').mean()
	consumption_col = weekly_df.columns[0]
	average_weekly = weekly_df[consumption_col].mean()
	weekly_df['Consumption'] = weekly_df[consumption_col].apply(lambda x: 'Alto' if x > average_weekly else 'Basso')
	weekly_out = os.path.join(output_folder, f"{file_name}_weekly_high_low.csv")
	weekly_df.to_csv(weekly_out, index=True)

