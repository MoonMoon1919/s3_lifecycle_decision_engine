"""
calculates number of days in two storage classes

input:
- number of days in first storage class
- number of days total

output:
- months total
- months in first storage class
- months in second storage class
"""


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


# N, number of days in first storage class
# Z, number of days object will exist
# Y, number of days object will exist in second storage class
n = 14
z = 365
y = z - n

n = calculate_months(n)
z = calculate_months(z)
y = calculate_months(y)

print(n, z, y)
