# S3 Lifecycle Policy Decision Engine

A really fancy title for a simple python script that determines if a lifecycle policy will be effective for your S3 bucket

Disclaimer: The financial results returned from this are not guaranteed to be accurate, but exist to serve as a baseline in your decision making process of if you should implement a lifecycle policy (or remove your existing one).

Requirements:
- Python 3.7

CLI args
```
--starting_storage_class (--ssc)
--target_storage_class (--tsc)
--total_storage_gb (--tsg)
--number_objs (--nobss)
--data_retrieved_gb (--drg)
--initial_storage_class_days (--iscd)
--total_days (--td)
```

Usage
```
python3 main.py --ssc <starting storage class> --tsc <target storage class> --tsg <size in gb> --drg <data in gb retrieved> --iscd <number of days in starting storage class> --td <number of days to model> --nobj <number of objects stored>
```