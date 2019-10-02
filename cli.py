"""
CLI implementation for calculator.

input:
- starting_storage_class
- target_storage_class
- total_storage_gb
- number_objs
- data_retrieved_gb
- initial_storage_class_days
- days_before_expiration
"""

from argparse import ArgumentParser

# Initial parser implementation
parser = ArgumentParser(
    description="CLI tool for caclulating if it's necessary to implement a lifecycle policy for an S3 bucket"
)

# Add arguments
parser.add_argument(
    "--starting_storage_class",
    "--ssc",
    choices=["standard", "standard_ia", "standard_ia_one_zone"],
    type=str,
    help="S3 Storage class that objects are being stored in initially",
    required=True,
)
parser.add_argument(
    "--target_storage_class",
    "--tsc",
    choices=["standard_ia", "standard_ia_one_zone", "glacier", "glacier_deep_archive"],
    type=str,
    help="s3 Storage class that objects will reside in after lifecycle policy",
    required=True,
)
parser.add_argument(
    "--total_storage_gb",
    "--tsg",
    type=float,
    help="Total number of GB stored in S3 over the course of one month",
    required=True,
)
parser.add_argument(
    "--number_objs",
    "--nobj",
    type=int,
    help="Number of objects that will be stored",
    required=True,
)
parser.add_argument(
    "--data_retrieved_gb",
    "--drg",
    type=float,
    help="Total number of GB to be retrieved from secondary storage class over on month",
)
parser.add_argument(
    "--initial_storage_class_days",
    "--iscd",
    type=int,
    help="Number of days objects will be stored in initial storage class",
    required=True,
)
parser.add_argument(
    "--total_days",
    "--td",
    type=int,
    help="Numnber of days objects will exist in this context (theoretically before they are expired)",
    required=True,
)

ARGS = parser.parse_args()
