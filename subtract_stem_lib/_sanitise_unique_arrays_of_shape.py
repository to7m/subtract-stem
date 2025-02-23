import numpy as np

from ._sanitisation import sanitise_arg as san


_dtypes_for_dtype_names = {
    "bool": bool, "float": np.float32, "complex": np.complex64
}


def sanitise_unique_arrays_of_shape(
    *, array_infos, reference_shape, reference_name
):
    for arr, name, dtype_name in array_infos:
        dtype = _dtypes_for_dtype_names[dtype_name]

        if arr is None:
            arr = np.empty(reference_shape, dtype=dtype)
        else:
            sanitiser_name = f"array_{len(reference_shape)}d_{dtype_name}"
            san(name, sanitiser_name)

            if arr.shape != reference_shape:
                raise ValueError(
                    f"{name!r} should have same shape as {reference_name}"
                )

        yield arr
