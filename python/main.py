# import numpy as np
# import matplotlib.pyplot as plt
# import multiprocessing as mp
# from itertools import product

# def compute_mandelbrot(max_iter, mode):
#     width, height = 800, 600
#     xmin, xmax = -2.1, 0.6
#     ymin, ymax = -1.2, 1.2
    
#     if mode == "serial":
#         mandelbrot_set = mandelbrot_set_serial
#     elif mode == "parallel":
#         mandelbrot_set = mandelbrot_set_parallel
#     else:
#         print("Invalid mode. Please specify 'serial' or 'parallel'.")
#         return
    
#     if mode == "parallel":
#         with mp.Pool() as pool:
#             results = pool.starmap(mandelbrot_set, product([(xmin, xmax, ymin, ymax, width, height, max_iter)]))
#             mandelbrot_data = np.concatenate(results)
#     else:
#         mandelbrot_data = mandelbrot_set(xmin, xmax, ymin, ymax, width, height, max_iter)
    
#     plt.imshow(mandelbrot_data.T, extent=(xmin, xmax, ymin, ymax), cmap='hot', interpolation='nearest')
#     plt.colorbar()
#     # plt.savefig(f"mandelbrot_{mode}.png")
#     plt.show()

# def mandelbrot_set_serial(xmin, xmax, ymin, ymax, width, height, max_iter):
#     x = np.linspace(xmin, xmax, width)
#     y = np.linspace(ymin, ymax, height)
#     mandelbrot_data = np.zeros((width, height))
    
#     for i in range(width):
#         for j in range(height):
#             c = x[i] + 1j * y[j]
#             z = 0
#             for k in range(max_iter):
#                 z = z**2 + c
#                 if abs(z) > 2:
#                     mandelbrot_data[i, j] = k
#                     break
    
#     return mandelbrot_data

# def mandelbrot_set_parallel(args):
#     xmin, xmax, ymin, ymax, width, height, max_iter = args
#     x = np.linspace(xmin, xmax, width)
#     y = np.linspace(ymin, ymax, height)
#     mandelbrot_data = np.zeros((width, height))
    
#     def compute_pixel(i, j):
#         c = x[i] + 1j * y[j]
#         z = 0
#         for k in range(max_iter):
#             z = z**2 + c
#             if abs(z) > 2:
#                 return i, j, k
#         return i, j, max_iter
#     with mp.Pool() as pool:
#         results = pool.starmap(compute_pixel, product(range(width), range(height)))
    
#         for result in results:
#             i, j, k = result
#             mandelbrot_data[i, j] = k
        
#         return mandelbrot_data

import matplotlib.pyplot as plt
from functools import partial
import multiprocessing
import numpy as np

def mandelbrot_calculate(yPos, h, w, max_iteration=1000):
    y0 = yPos * (2/float(h)) - 1  # rescale to -1 to 1
    row = []
    for xPos in range(w):
        x0 = xPos * (3.5/float(w)) - 2.5  # rescale to -2.5 to 1
        iteration, z = 0, 0 + 0j
        c = complex(x0, y0)
        while abs(z) < 2 and iteration < max_iteration:
            z = z**2 + c
            iteration += 1
        row.append(iteration)

    return row

def mandelbrot_serial(max_iteration):
    w, h = 800, 600
    partial_row = partial(mandelbrot_calculate, h=h, w=w, max_iteration=max_iteration)
    mandelImg = map(partial_row, range(h))
    return list(mandelImg)  # Convert map object to a list of lists

def mandelbrot_parallel(max_iteration):
    w, h = 800, 600
    partial_row = partial(mandelbrot_calculate, h=h, w=w, max_iteration=max_iteration)
 
    with multiprocessing.Pool() as pool:
        mandelImg = pool.map(partial_row, range(h))  # Use pool.map to parallelize calculation
 
    return mandelImg

def compute_mandelbrot(max_iter, mode):
    if mode == "serial":
        img = mandelbrot_serial(max_iter)
    elif mode == "parallel":
        img = mandelbrot_parallel(max_iter)
    else:
        print("Invalid mode. Please specify 'serial' or 'parallel'.")
        return
    
    img = np.array(img, dtype=float)  # Convert list of lists to numpy array of floats
    img = np.log(np.array(img))  # Take logarithm to emphasize details
    
    plt.imshow(img, cmap='RdPu', extent=[-2.5, 1, -1.5, 1.5])
    plt.title(f"Mandelbrot Set (Max Iterations: {max_iter})")
    plt.show()


if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "serial"
    max_iter = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
    
    compute_mandelbrot(max_iter, mode)
