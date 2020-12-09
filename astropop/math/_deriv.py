"""Function derivatives for error propagation."""

import sys
import numpy as np
import copy


__all__ = ['derivatives', 'propagate_2']


STEP_SIZE = np.sqrt(sys.float_info.epsilon)


@np.vectorize
def _deriv_pow_0(x, y):
    """Partial derivative of x**y in x."""
    if y == 0:
        return 0.0
    elif x != 0 or y % 1 == 0:
        return y*x**(y-1)
    else:
        return numerical_derivative(np.pow, 0)(x, y)


@np.vectorize
def _deriv_pow_1(x, y):
    """Partial derivative of x**y in y."""
    if x == 0 and y > 0:
        return 0.0
    else:
        return np.log(x)*x**y


def _deriv_mod_1(x, y):
    """Partial derivative of x%y in y."""
    # if x % y < STEP_SIZE:
    #     return STEP_SIZE
    # else:
    #     return numerical_derivative(np.mod, 1)(x, y)
    return numerical_derivative(np.mod, 1)(x, y)


# Function partial derivatives for x and y
derivatives = {
    'add': (lambda x, y: 1.0,
            lambda x, y: 1.0),
    'sub': (lambda x, y: 1.0,
            lambda x, y: -1.0),
    'div': (lambda x, y: 1/y,
            lambda x, y: -x/(y**2)),
    'truediv': (lambda x, y: 1/y,
                lambda x, y: -x/(y**2)),
    'floordiv': (lambda x, y: 0.0,
                 lambda x, y: 0.0),
    'mod': (lambda x, y: 1.0,
            _deriv_mod_1),
    'mul': (lambda x, y: y,
            lambda x, y: x),
    'pow': (_deriv_pow_0, _deriv_pow_1),
    # 'abs': (lambda x: 1.0 if x >= 0 else -1.0),
    # 'neg': (lambda x: -1.0),
    # 'pos': (lambda x: 1.0),
    # 'trunc': (lambda x: 0.0)
}


def propagate_2(func, fxy, x, y, sx, sy):
    """Propagate errors using function derivatives.

    Parameters
    ----------
    func: string
        Function name to perform error propagation. Must be in derivatives
        keys.
    fxy: float or array_like
        Numerical result of f(x, y).
    x, y: float or array_like
        Variables of the function.
    sx, sy: float or array_like
        1-sigma errors of the function variables.

    Returns
    -------
    sf: float or array_like
        1-sigma uncorrelated error associated to the operation.
    """
    if func not in derivatives.keys():
        raise ValueError(f'func {func} not in derivatives.')

    deriv_x, deriv_y = derivatives[func]
    try:
        del_x2 = np.square(deriv_x(x, y))
        del_y2 = np.square(deriv_y(x, y))
        sx2 = np.square(sx)
        sy2 = np.square(sy)
        sf = np.sqrt(del_x2*sx2 + del_y2*sy2)
        return sf
    except (ValueError, ZeroDivisionError, OverflowError):
        shape = np.shape(fxy)
        if len(shape) == 0:
            return np.nan
        else:
            return np.empty(shape).fill(np.nan)


def numerical_derivative(func, arg_ref, step=STEP_SIZE):
    """Create a function to compute a numerical derivative of func.

    Parameters
    ----------
    func: callable
        The function to compute the numerical derivative.
    arg_ref: int or string
        Variable to be used for diferentiation. If int, a position will be
        used. If string, a variable name will be used.
    step: float (optional)
        Epsilon to compute the numerical derivative, using the
        (-epsilon, +epsioln) method.

    Returns
    -------
    derivative_wrapper: callable
        Partial derivative function.

    Notes
    -----
    - Implementation based on `uncertainties` package.
    """
    if not callable(func):
        raise ValueError(f'function {func} not callable.')

    # If reference variable is in kwargs (str) instead of args (int).
    change_kwargs = isinstance(arg_ref, str)

    @np.vectorize
    def derivative_wrapper(*args, **kwargs):
        """
        Partial derivative, calculated with the (-epsilon, +epsilon)
        method, which is more precise than the (0, +epsilon) method.
        """
        # Compute the epsilon relative to the variyng parameter
        if change_kwargs:
            var_v = kwargs[arg_ref]
        else:
            var_v = args[arg_ref]

        eps = step*abs(var_v)
        if not eps:
            # Arbitrary, but "small" with respect to 1:
            eps = step

        # Copy args and assing the variable function with values plus
        # and minus the epsilon
        # This will cause more memory to be used, but do not change the
        # original objects.
        kwargs_p = copy.copy(kwargs)
        kwargs_m = copy.copy(kwargs)
        args_p = list(args)
        args_m = list(args)

        if change_kwargs:
            kwargs_p[arg_ref] += eps
            kwargs_m[arg_ref] -= eps
        else:
            args_p[arg_ref] += eps
            args_m[arg_ref] -= eps

        # Compute the function values with shifted vvariable
        f_plus = func(*args_p, **kwargs_p)
        f_minus = func(*args_m, **kwargs_m)

        return (f_plus - f_minus)/2/eps

    return derivative_wrapper
