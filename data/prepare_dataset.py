from data_synthesis import generate_uk_credit_dataset_with_score_factors
# Load the dataset
df = generate_uk_credit_dataset_with_score_factors("archive/accepted_2007_to_2018Q4 2.csv", sample_size=1000)

# Preview first few rows
print(df.head())

# Save to file if needed
df.to_csv("uk_credit_dataset.csv", index=False)
