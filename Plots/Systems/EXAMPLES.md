## PREDATOR PREY MODEL
'''
# f_x: R x R x R -> R
# dx/dt = f_x(t, x, y)
def f_x(t, x, y):
    growth_rate = 1.0
    predation_rate = 0.2
    death_rate = 0.2 
    return growth_rate * x - predation_rate * x * y - death_rate * x 


# g_y: R x R x R -> R
# dy/dt = g_y(t, x, y)
def g_y(t, x, y):
    predator_efficiency = 0.2
    death_rate = 0.4
    return predator_efficiency * x * y - death_rate * y
'''

## HOPF BIFURCATION MODEL
'''
mu = -2.0
alpha = 1.0
beta = 0.3
omega = 4.0

# f_x: R x R x R -> R
# dx/dt = f_x(t, x, y)
def f_x(t, x, y):
    return -mu*x*cos(x) - omega*y + alpha*x*(x**2 + y**2) - beta*x*(x**2 + y**2)**2/t


# g_y: R x R x R -> R
# dy/dt = g_y(t, x, y)
def g_y(t, x, y):
    return omega*x - mu*y*sin(y) + alpha*y*(x**2 + y**2) - beta*y*(x**2 + y**2)**2/t
'''

## MACHINE LEARNING MODEL
'''
# f_x: R x R x R -> R
# dx/dt = f_x(t, x, y)
def f_x(t, x, y):
    return y


# g_y: R x R x R -> R
# dy/dt = g_y(t, x, y)
def g_y(t, x, y):
    n = 1
    return -(2 / (t + 0.001)) * y - x ** n
'''