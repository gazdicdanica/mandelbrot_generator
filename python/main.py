
import matplotlib.pyplot as plt
from functools import partial
import multiprocessing
import numpy as np
import time

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

def mandelbrot_serial(max_iteration, w, h):
    start_time = time.time()
    partial_row = partial(mandelbrot_calculate, h=h, w=w, max_iteration=max_iteration)
    mandelImg = list(map(partial_row, range(h)))
    end_time = time.time()
    print(f"Mode: Serial\tWidth: {w}\tHeight: {h}\tTime: {end_time - start_time:.4f} seconds")
    return mandelImg  


def mandelbrot_parallel(max_iteration, w, h, num_processes):
    start_time = time.time()
    partial_row = partial(mandelbrot_calculate, h=h, w=w, max_iteration=max_iteration)
 
    if num_processes is None:
        num_processes = multiprocessing.cpu_count()
    
    with multiprocessing.Pool(processes=num_processes) as pool:
        mandelImg = pool.map(partial_row, range(h)) 
    end_time = time.time()

    print(f"Mode: Parallel\tWidth: {w}\tHeight: {h}\tNum of threads: {num_processes if num_processes != None else multiprocessing.cpu_count()}\t Time: {end_time - start_time:.4f} seconds")
    return mandelImg


def compute_mandelbrot(max_iter, mode, w, h, processes):
    if mode == "serial":
        img = mandelbrot_serial(max_iter, w, h)
    elif mode == "parallel":
        img = mandelbrot_parallel(max_iter, w, h, processes)
    else:
        print("Invalid mode. Please specify 'serial' or 'parallel'.")
        return
    
    img = np.array(img, dtype=float)  
    img = np.log(np.array(img)) 
    
    plt.imshow(img, cmap='RdPu')
    plt.savefig(f"../data/python/{mode}.png")
    # plt.show()

    


if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "serial"
    max_iter = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    w = int(sys.argv[3]) if len(sys.argv) > 3 else 800
    h = int(sys.argv[4]) if len(sys.argv) > 4 else 500

    processes = None
    if mode == "parallel":
        processes = int(sys.argv[5]) if len(sys.argv) > 5 else None
    
    compute_mandelbrot(max_iter, mode, w, h, processes)
