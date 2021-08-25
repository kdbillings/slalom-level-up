"""
https://projecteuler.net/problem=267

You are given a unique investment opportunity.
Starting with £1 of capital, you can choose a fixed proportion, f, of your capital to bet on a fair coin toss repeatedly for 1000 tosses.
Your return is double your bet for heads and you lose your bet for tails.
For example, if f = 1/4, for the first toss you bet £0.25, and if heads comes up you win £0.5 and so then have £1.5. You then bet £0.375 and if the second toss is tails, you have £1.125.
Choosing f to maximize your chances of having at least £1,000,000,000 after 1,000 flips, what is the chance that you become a billionaire?
All computations are assumed to be exact (no rounding), but give your answer rounded to 12 digits behind the decimal point in the form 0.abcdefghijkl.
"""


from numpy import log as ln
from math import comb, ceil

"""
The expected result of n throws of a coin is binomial problem. 
If every bet was 1 lb and we threw 1000 times, our expected payout would be 500. 
E(X) = n * p where n is number of throws and p is probability of success, .5

But our bet changes after each throw. 

So we are in a binomial tree situation.We basically need to figure out the minimum number of heads needed
to get to 1 billion lbs. 

Our total winnings can be expressed using the binomial tree formula used for options pricing
Ugh, I hated this part of actuarial science. But the math is fun.

S_{n}=S_{0} * u^{N_{u}-N_{d}}

If S is price of the option after it moves up or down by a specific factor (u or d) per step of the tree.
So after n branchings, the price will be
S_n = S_0 * u^(N_u - N_d)
where N_u is number of up ticks and N_d is the number of down ticks.
From Wikipedia: https://en.wikipedia.org/wiki/Binomial_options_pricing_model

This doesn't quite work, because we don't either win our bet or lose our bet. u is not consistent.
We win twice our bet (in addition to the money bet, not lost) or lose our bet. 

So we separate out u into wins and losses.

S_n = s_0 * u_u^N_u * u_d^N_d

So we know the following variables:
n is 1000 flips
S_0 is our starting value of 1 pound
S_n is 1 billion pounds, or 10^9
u_u ,the proportion increased on heads, is 1+2f
u_d, the proportion decreased on tails, is 1-1f
We also know that N_d = 1000 - N_u, and since we're solving for N_u, the minimum number of heads, let's call that x.
That leaves us with the following equation:

10^9 = 1 * (1+ 2f)^(x) * (1-f)^(1000-x)

We want to solve for x so that we can find the value of f that minimizes x. 

10^9 = (1+ 2f)^(x) * (1-f)^(1000-x)

Omg I forgot how to solve for an exponent. This hurts.
ln(x * y) = lnx + lny
ln(e^x) = x
𝑥𝑛=𝑦 => log𝑥𝑛=log𝑦

take the natural log of both sides:
9ln(10) = x * ln(1 + 2f) + (1000 - x)* ln(1 - f)
9ln(10) = x (ln(1 + 2f) - ln(1 - f)) + 1000ln(1 - f)
x (ln(1 + 2f) - ln(1 - f)) = 9ln(10) -1000ln(1 - f)
x = ((9ln(10) - 1000ln(1-f)) / (ln(1+2f) - ln(1-f))

so we need to solve for the f that minimizes x

This should be only one local minimum. I can't imagine this equation has more than one.
You wouldn't think raising your proportition past some minimum would generate another minimum.
This function isn't linear, but I think it's a parabola with one dip or peak, just logically. 
That makes it easier to assume. We can solve with an algorithm rather than remembering diffeq

Let's go with what I remember of lagrange multiplier algorithms.
"""

# have to start guessing somewhere
initial_f = .5
# let's move around in big chunks to find the minimum, and get smaller and smaller chunks until we hit
# the required accuracy
initial_d = .1
# required accuracy
min_d = 10**-12


# here we have a function for finding x (min number of heads to get to a billion pounds) given some f
def find_x(f):
    return ((9*ln(10)) - (1000 * ln(1-f))) / (ln(1 + 2*f) - ln(1-f))


# we have to figure out which direction to go in initially and then every time we
# make our precision of guess smaller
def get_initial_direction(x, f, d):
    x_with_more_f = find_x(f + d)
    x_with_less_f = find_x(f - d)

    # we want the lowest x

    if x_with_more_f > x and x > x_with_less_f:
        return -1
    if x_with_more_f < x and x < x_with_less_f:
        return 1
    else:
        return 0

# this function keeps moving along the function until x doesn't get smaller
# , indicating we're close to a minimum
def get_low_until_you_cant_no_mow(x, f, d):
    initial_direction = get_initial_direction(x, f, d)
    if initial_direction == 0:
        return x, f, d

    new_f = f + (initial_direction * d)
    new_x = find_x(new_f)
    while new_x < x:
        new_f = new_f + (initial_direction * d)
        x = new_x
        new_x = find_x(new_f)
        print(f"x: {x}, f: {f}, d: {d}")
    print(f"final x: {x}, f: {f}, d: {d}")
    return x, new_f, d

# starting variables
x = find_x(initial_f)
f = initial_f
d = initial_d

# while d is greater than or equal to maximum accuracy required
# run get_low_until_you_cant_no_mow, make our guessing delta chunck smaller, and run it again
print(f"x: {x}, f: {f}, d: {d}")
while d >= min_d:
    x, f, d = get_low_until_you_cant_no_mow(x, f, d)
    # shrink that delta and find the local minimum
    d = d * .1
    print(f"new d:{d}")

# final minimum x, f, and d
print(f"x: {x}, f: {f}, d: {d}")

# We need a min number of flips, so take the ceiling of x
round_x = ceil(x)

# next calculate the probability of getting x heads in 1000 flips. This is basic binomial distribution.
# the standard equation where n = total trials, k is successes, and p is probability of success
# (n choose k) * p^k * (1-p)^(n-k)

# this is the probability of getting exactly round_x flips
# probability = comb(1000,round_x) * (.5**round_x) * ((1-.5)**(1000-round_x))

def get_prob_x_heads(x):
    return comb(1000,x) * (.5**x) * ((1-.5)**(1000-x))


# but we want to know the probability of getting AT LEAST x heads in 1000 flips (and thus winning at least a billion dollars)
# so now we gotta add em all up past the round_x all the way to 1000 flips in a row.
probability = 0
while round_x <= 1000:
    probability = probability + get_prob_x_heads(round_x)
    round_x = round_x + 1

print(f"probability: {probability}")
# 0.9999928361867136










