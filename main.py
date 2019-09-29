"""Module for helping calculate if implementing a S3 lifecycle policy will be necessary and cost effective."""

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
}

avg_monthly_days = 30.42


def s3_lifecycle_necessary(
    storage_type_initial=None,
    storage_type_transition=None,
    number_objs=None,
    total_storage_gb=None,
    data_retrieval_gb=None,
    days_before_transition=None,
    days_before_expiration=None,
):
    """
    Function that determines if implementing an S3 Lifecycle policy will be necessary
    """
    sti = data[storage_type_initial]
    stt = data[storage_type_transition]

    # Months Till Expiration
    mte = days_before_expiration / avg_monthly_days

    # Additional storage cost post transition
    asc = 0

    tco_mte_multiplier = 1

    # Glacier adds 40kb of metadata per object, 32kb at glacier pricing and 8kb at standard storage
    if storage_type_transition == "glacier":
        smd = (number_objs * 0.000008) * data["standard"]["price_per_gb"]
        gmd = (number_objs * 0.000032) * stt["price_per_gb"]
        asc = smd + gmd

        if (days_before_expiration - days_before_transition) < 90:
            tco_mte_multiplier = 2

    # Calculate the price of storing the data in it's current storage class
    # Monthly Cost Initial
    mci = total_storage_gb * sti["price_per_gb"]

    # Calculate the cost of transitioning the objects from current storage class to new storage class
    # Transition Cost
    tc = (number_objs / stt["items_per_transition_chunk"]) * stt["transition_cost"]

    # Calculate the storage cost in the new storage class
    # New Storage Costs
    nsc = (total_storage_gb * stt["price_per_gb"]) + asc

    # Calculate the cost of data retrieval from the new storage class
    # Retrieval cost
    rc = data_retrieval_gb * 0.01

    # Calculate the charge of one month in storage, the transition, and data retrieval for one month
    # Storage cost and transition
    scat = tc + nsc + rc

    # Calculate the TCO in current storage class
    tco_current_class = mci * mte

    # Calculate TCO after transition
    tco_transition_class = mci + scat + (nsc * (mte - tco_mte_multiplier))

    print("Monthly Cost in %s: %f" % (storage_type_initial, mci))
    print("First month cost in %s: %f" % (storage_type_transition, scat))
    print("Monthly cost in %s: %f" % (storage_type_transition, nsc))
    print("TCO in %s: %f" % (storage_type_initial, tco_current_class))
    print(
        "TCO after transition to %s: %f"
        % (storage_type_transition, tco_transition_class)
    )
    print("\n")

    if tco_current_class > tco_transition_class:
        print("Lifecycle policy transition will be more cost effective")
        return True
    else:
        print("Keeping storage as is will be more cost effective")
        return False


if __name__ == "__main__":
    s3_lifecycle_necessary(
        storage_type_initial="standard",
        storage_type_transition="glacier",
        number_objs=10000,
        total_storage_gb=10,
        data_retrieval_gb=1,
        days_before_transition=30,
        days_before_expiration=150,
    )
