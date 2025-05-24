import pandas as pd
import time
import os
from datetime import datetime, timedelta

class PositionLogger:
	def __init__(self, position_file="position_data.csv", signal_dir="signal_data/", save_dir="position_logging/", monitor_duration=30):

		self.position_file = position_file
		self.signal_dir = signal_dir
		self.save_dir = save_dir


		self.monitor_duration = timedelta(minutes=monitor_duration)
		self.start_times = {}
		self.data_store = {}

	def store_data(self):
		positions = pd.read_csv(self.position_file)
		for _, row in positions.iterrows():
			pair = row["symbol"]
			self.start_times[pair] = pd.to_datetime(row["dtime"])

			signal_file = os.path.join(self.signal_dir, f"{pair}_signal.csv")

			data = pd.read_csv(signal_file)
			recent_time = pd.to_datetime(data.iloc[-1]["dtime"])
			time_diff = recent_time - self.start_times[pair]
			if time_diff == self.monitor_duration:  # 30 min time difference
				save_path = os.path.join(self.save_dir, f"{pair}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_log.csv")
				data.to_csv(save_path, index=False)

		# positions.to_csv(self.position_file, index=False)

if __name__ == "__main__":
	logger = PositionLogger("./test_position_files/positions.csv")
	logger.store_data()


# Dictionary to store data
# data_store = {}

# # Set monitoring duration
# monitor_duration = timedelta(minutes=30)

# # Track start times
# start_times = {}

# Initialize start times for each position
# for _, row in positions.iterrows():
#     pair = row["pair"]
#     start_times[pair] = datetime.now()
#     data_store[pair] = []

# # Monitoring loop
# while True:
#     current_time = datetime.now()
#     completed_positions = []

#     for _, row in positions.iterrows():
#         pair = row["pair"]
#         signal_file = os.path.join(signal_dir, f"{pair}_signal.csv")

#         # Check if monitoring time has passed
#         if current_time - start_times[pair] >= monitor_duration:
#             completed_positions.append(pair)
#             continue

#         # Read latest signal data if file exists
#         if os.path.exists(signal_file):
#             signal_data = pd.read_csv(signal_file)
#             latest_data = signal_data.iloc[-1].to_dict()
#             data_store[pair].append(latest_data)

#     # Remove completed positions
#     if completed_positions:
#         positions = positions[~positions["pair"].isin(completed_positions)]
#         positions.to_csv(position_file, index=False)

#         for pair in completed_positions:
#             save_path = f"saved_data/{pair}_saved.csv"
#             pd.DataFrame(data_store[pair]).to_csv(save_path, index=False)
#             print(f"Saved data for {pair} and removed from position_data.csv")

#     # Exit if all positions are processed
#     if positions.empty:
#         print("All positions processed. Exiting...")
#         break

#     # Wait for next update (adjust timing as needed)
#     time.sleep(60)  # Check every minute
