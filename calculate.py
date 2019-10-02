"""
input:
- months total
- months in first storage class
- months in second storage class
- number of objects
- size total
"""

data = {
    "standard": {"price_per_gb": 0.023},
    "standard_ia": {
        "price_per_gb": 0.0125,
        "transition_cost": 0.01,
        "items_per_transition_chunk": 1000,
        "data_retrieval_cost_per_gb": 0.01,
    },
    "standard_ia_one_zone": {
        "price_per_gb": 0.01,
        "transition_cost": 0.01,
        "items_per_transition_chunk": 1000,
        "data_retrieval_cost_per_gb": 0.01,
    },
    "glacier": {
        "price_per_gb": 0.004,
        "transition_cost": 0.05,
        "items_per_transition_chunk": 1000,
        "data_retrieval_cost_per_gb": 0.01,
    },
    "glacier_deep_archive": {
        "price_per_gb": 0.00099,
        "transition_cost": 0.05,
        "items_per_transition_chunk": 1000,
        "data_retrieval_cost_per_gb": 0.02,
    },
}


def calculate_months(days: int = 12) -> float:
    """
    Calculates number of months from input of 'days', using the average number of days in a normal year.

    This represents the expected lifetime of an object in S3 before it is expired
    By default it is set to one year, to provide forcasting abilities for folks who aren't deleting things

    Args:
        days: Number of days objects will exist in total

    Returns:
        Int, number of months calculated from days
    """
    days_per_month = 30.416666666666668

    return days / days_per_month


def calculate_data_retrieval_cost(
    months: int, target_storage_class: str, data_retrieved_gb: float
) -> float:
    """
    Calculates the potential cost of data retrieval over a given time period in months, default is 12 months
    """
    target_storage_class_data = data[target_storage_class]

    retrieval_cost = (
        data_retrieved_gb * target_storage_class_data["data_retrieval_cost_per_gb"]
    ) * months

    return retrieval_cost


def calculate_transition_cost(number_objs: int, target_storage_class: str) -> float:
    """
    Calculates the cost of transition data from one class to another
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
    """
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


def main() -> bool:
    """
    .
    """
    starting_storage_class = "standard"
    target_storage_class = "glacier"
    total_storage_gb = 1000
    number_objs = 1000000
    data_retrieved_gb = 1

    initial_storage_class_days = 30
    total_days = 90
    target_storage_class_days = total_days - initial_storage_class_days

    initial_storage_class_months = calculate_months(initial_storage_class_days)
    total_months = calculate_months(total_days)
    target_storage_class_months = calculate_months(target_storage_class_days)

    storage_cost_no_transition = calculate_storage_cost(
        months=total_months,
        storage_class=starting_storage_class,
        total_storage_gb=total_storage_gb,
        number_objs=number_objs,
    )

    inital_storage_cost = calculate_storage_cost(
        months=initial_storage_class_months,
        storage_class=starting_storage_class,
        total_storage_gb=total_storage_gb,
        number_objs=number_objs,
    )

    target_storage_cost = calculate_storage_cost(
        months=target_storage_class_months,
        storage_class=target_storage_class,
        total_storage_gb=total_storage_gb,
        number_objs=number_objs,
    )

    target_transition_cost = calculate_transition_cost(
        number_objs=number_objs, target_storage_class=target_storage_class
    )

    target_retrieval_cost = calculate_data_retrieval_cost(
        months=target_storage_class_months,
        target_storage_class=target_storage_class,
        data_retrieved_gb=data_retrieved_gb,
    )

    lifecycle_policy_cost = (
        inital_storage_cost
        + target_storage_cost
        + target_transition_cost
        + target_retrieval_cost
    )

    print("Lifecycle policy cost: %f" % lifecycle_policy_cost)
    print("Storage cost in current class: %f" % storage_cost_no_transition)

    return True


if __name__ == "__main__":
    main()
