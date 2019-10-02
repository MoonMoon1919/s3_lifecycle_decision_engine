"""
input:
- starting_storage_class
- target_storage_class
- total_storage_gb
- data_retrieved_gb
- initial_storage_class_days
- days_before_expiration
"""

# Import our CLI args
from cli import ARGS
from s3_data import data


def calculate_months(days: int) -> float:
    """
    Calculates number of months from input of 'days', using the average number of days in a normal year.

    This represents the expected lifetime of an object in S3 before it is expired
    By default it is set to one year, to provide forcasting abilities for folks who aren't deleting things

    Args:
        days: Number of days objects will exist in total

    Returns:
        int, number of months calculated from days
    """
    days_per_month = 30.416666666666668

    return days / days_per_month


def calculate_data_retrieval_cost(
    months: int, target_storage_class: str, data_retrieved_gb: float
) -> float:
    """
    Calculates the potential cost of data retrieval over a given time period in months, default is 12 months

    Args:
        months: number of months objects will exist, target_storage_class_months is used for this
        target_storage_class: the S3 storage class that is being targeted
        data_retrieved_gb: number of gb retrieved per month

    Returns:
        int, the total cost of data retrieval over the course of the lifetime of the object in the secondary storage class
    """
    target_storage_class_data = data[target_storage_class]

    retrieval_cost = (
        data_retrieved_gb * target_storage_class_data["data_retrieval_cost_per_gb"]
    ) * months

    return retrieval_cost


def calculate_transition_cost(number_objs: int, target_storage_class: str) -> float:
    """
    Calculates the cost of transition data from one class to another

    Args:
        number_objs: the number of objects that are added on a monthly basis
        target_storage_class: the storage class the objects will reside in after they are transitioned

    Returns:
        int, the cost of the transition
    """
    target_storage_class_data = data[target_storage_class]

    transition_cost = (
        number_objs / target_storage_class_data["items_per_transition_chunk"]
    ) * target_storage_class_data["transition_cost"]

    return transition_cost


def calculate_storage_cost(
    months: float, storage_class: str, total_storage_gb: int, number_objs: int
) -> float:
    """
    Calculates storage cost for a given storage class

    Args:
        months: number of months
        storage_class: The storage class
        total_storage_gb: total number of gb that will be stored
    
    Returns:
        float: cost of storage in the specified class
    """
    # Number of days in an average month, used in glacier 90 day minimum calculation
    days_per_month = 30.416666666666668
    storage_class_data = data[storage_class]

    # In Glacier, each object has 40kb of metadata associated with it, defaults to 0
    metadata_storage_cost = 0

    if storage_class == "glacier":
        # 8kb per object in Standard
        standard_metadata = (number_objs * 0.000008) * data["standard"]["price_per_gb"]

        # 32kb per object in Glacier
        glacier_metadata = (number_objs * 0.000032) * storage_class_data["price_per_gb"]

        # Calculate the metadata_storage_cost by adding the above together
        metadata_storage_cost = standard_metadata + glacier_metadata

        # In glacier you are charged for 90 days of storage at a minimum, post transition
        if (months / days_per_month) < 90.00:
            months: 3.0

    # Total cost in in the given storage class for given months (can be partial months)
    storage_cost = (
        (total_storage_gb * storage_class_data["price_per_gb"]) + metadata_storage_cost
    ) * months

    return storage_cost


def handler(
    starting_storage_class: str,
    target_storage_class: str,
    total_storage_gb: float,
    number_objs: int,
    data_retrieved_gb: float,
    initial_storage_class_days: int,
    total_days: int,
) -> bool:
    """
    Main entrypoint for the calculator

    Args:
        starting_storage_class: the initial storage class the objects will be stored in
        target_storage_class: the secondary storage class the objects will be stored in after transition
        total_storage_gb: the total storage in gb that will be stored
        number_objs: the total of number of objects that will be added over a month
        data_retrieved_gb: the amount of data in gb that will be retrieved from the second storage class after transition
        initial_storage_class_days: the number of days objects will exist in the initial storage class before transition
        total_days: the number of days objects will exist (theoretically before they are expired)

    Returns:
        bool, the core decision can be deduced from what is printed to the console
    """
    # Calculate the amount of days objects will be in the target storage class
    # This is based on the number of days the object exists (total_days) and the number of days
    # the object will be in the intial storage class
    target_storage_class_days = total_days - initial_storage_class_days

    # Calculate the number of months, based on input days
    initial_storage_class_months = calculate_months(initial_storage_class_days)
    total_months = calculate_months(total_days)
    target_storage_class_months = calculate_months(target_storage_class_days)

    # Calculate the storage cost for the initial storage class over the entire life of the objects
    # This is used as the baseline comparison to see if a lifecycle policy will help or hinder in spend
    storage_cost_no_transition = calculate_storage_cost(
        months=total_months,
        storage_class=starting_storage_class,
        total_storage_gb=total_storage_gb,
        number_objs=number_objs,
    )

    # Calculate the storage cost in the initial storage class, taking account for the number of months it will be in there
    inital_storage_cost = calculate_storage_cost(
        months=initial_storage_class_months,
        storage_class=starting_storage_class,
        total_storage_gb=total_storage_gb,
        number_objs=number_objs,
    )

    # Calculate the storage cost in the secondary storage class
    target_storage_cost = calculate_storage_cost(
        months=target_storage_class_months,
        storage_class=target_storage_class,
        total_storage_gb=total_storage_gb,
        number_objs=number_objs,
    )

    # Calculate the cost of the transition
    target_transition_cost = calculate_transition_cost(
        number_objs=number_objs, target_storage_class=target_storage_class
    )

    # Calculate the cost of retrieval from secondary storage class
    target_retrieval_cost = calculate_data_retrieval_cost(
        months=target_storage_class_months,
        target_storage_class=target_storage_class,
        data_retrieved_gb=data_retrieved_gb,
    )

    # Calculate the total cost of ownership in the secondary storage class
    # This includes the initial time period
    lifecycle_policy_cost = (
        inital_storage_cost
        + target_storage_cost
        + target_transition_cost
        + target_retrieval_cost
    )

    # Print some data out informing the user of cost differences
    print(
        "Cost with lifecycle policy in multiple storage classes: %f"
        % lifecycle_policy_cost
    )
    print("Cost in current storage class: %f" % storage_cost_no_transition)

    print("\n")

    if storage_cost_no_transition > lifecycle_policy_cost:
        print("Implementing this lifecycle policy will be more cost effective")
    else:
        print("Retaining data in current storage class will be more effective")

    return True


if __name__ == "__main__":
    args = ARGS
    handler(
        starting_storage_class=args.starting_storage_class,
        target_storage_class=args.target_storage_class,
        total_storage_gb=args.total_storage_gb,
        number_objs=args.number_objs,
        data_retrieved_gb=args.data_retrieved_gb,
        initial_storage_class_days=args.initial_storage_class_days,
        total_days=args.total_days,
    )
