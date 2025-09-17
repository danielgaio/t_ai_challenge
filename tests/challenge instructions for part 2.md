FDE Live Coding Interview
# Objective
Our robotic arm's sorting function has been a great success in Thoughtful's robotic automation factory. Now, customers want to understand how their packages will be processed upfront. They have sent us CSV files with package details.
Your task is to analyze these packages, apply the sorting criteria using your existing function, and generate a comprehensive report. This report will show how their packages will be sorted and help them understand the efficiency and capacity of our robotic arm.
This challenge builds upon your initial sorting function, expanding its capabilities to meet real-world demand.
### Task Details

**Plan** (5 - 10 minutes)

- Read the instructions below and plan execution

**Data Ingestion** (15 - 20 minutes)

- Write code to read the data from `packages.csv` (below) and store it in an appropriate data structure for processing.
- Handle any data inconsistencies, errors, or missing values gracefully.

**Data Analysis and Reporting** (15 - 20 minutes)

- **Calculate Statistics**:
    - Total number of packages in the data artifact. This total is used in the statistics calculations for each stack.
    - Number and percentage of packages in each stack (`STANDARD`, `SPECIAL`, `REJECTED`).
    - Average, minimum, and maximum `Mass` and `Volume` for each stack.
- **Generate Summary Report**:
    - Display the statistics in a clear and organized format.
    - Ensure the report is easy to read and understand.
**Q&A** (5-10 mins)

- Spend a few minutes discussing potential improvements to the solution
    - How to handle extremely large datasets
        
        R: Use pandas `chunksize` parameter on the `read_csv()` function
        ```python
        import pandas as pd

        chunk_size = 100000  # Define the size of each chunk
        for chunk in pd.read_csv('your_large_file.csv', chunksize=chunk_size):
            # Process each chunk (e.g., filter, transform, write to a new file)
            # Example: Filter rows where 'value' is greater than 100
            filtered_chunk = chunk[chunk['value'] > 100]
            # Do something with filtered_chunk, e.g., append to a new CSV or database
        ```

    - Ways to enhance performance further
    
        R: Use multiprocessing to parallelize the sorting function calls

    - Additional features that could be added
    
        R: Add visualization of the statistics using libraries like Matplotlib or Seaborn

### Guidance

- **Resources**: You are allowed to look up syntax and documentation as needed during the exercise.
- **Evaluation Criteria**: Your work will be assessed on:
    - Functionality
    - Code quality
    - Pragmatic choices

### Artifact

```csv
Width,Height,Length,Mass
50,60,70,10
,None,50,5
200,100,50,25
150,150,150,30
60,80,100,-15
85,95,105,20
100,abc,100,40
20,30,40,0
95,105,115,24
100,100,100
45,55,65,12
-50,60,70,10
110,120,130,22
80,90,100,20,0
60,70,80,18
Width,Height,Length,Mass
140,150,160,35
70,80,90,15
,None,None,None
80,90,100,15
None,None,None,None
50,60,70,10
"100","100","100","40"
200,100,50,25
100,,100,40
30,40,50,5
150,150,150,30
55,65,75,14
60,80,100,15
90,100,110,26
100,100,100,40
85,80,75,14
20,30,40,8
70,65,60,12
90,95,100,20
55,50,45,10
65,75,85,16
,None,40,50,5
95,105,115,24
None,None,None,None
32,32,23ab,43
```