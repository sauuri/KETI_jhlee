"""
Design variable bounds for the EC Fan optimization problem.

** DO NOT CHANGE THE SEQUENCE OF VARIABLES **

DesignVariable : [LowerBound, UpperBound]

Note: Slot_Area >= 270 is treated as an inequality constraint (G(x) <= 0),
      not a bound constraint. See optimizer_2.py for implementation.
"""

from numpy import atleast_2d, array

bounds = atleast_2d(array(
    list(
        {
            "V_rotor_r1":  [0.1,  24.0],
            "V_Opening_A": [11.0, 15.0],
            "V_Opening_W": [0.9,   1.8],
            "V_Shoe_A":    [100., 112.],
            "V_Shoe_W":    [1.0,   1.9],
            "V_Tooth_W":   [5.0,   5.6],
        }.values()
    )
))

lb = bounds[:, 0]
ub = bounds[:, 1]
