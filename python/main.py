import matplotlib.pyplot as plt
import multiprocessing
import numpy as np
import time
from functools import partial
import sys


def mandelbrot_calculate(yPos, h, w, max_iteration, xmin, xmax, ymin, ymax):
    y0 = yPos * (ymax - ymin) / float(h) + ymin  
    row = []
    for xPos in range(w):
        x0 = xPos * (xmax - xmin) / float(w) + xmin 
        iteration, z = 0, 0 + 0j
        c = complex(x0, y0)
        while abs(z) < 2 and iteration < max_iteration:
            z = z**2 + c
            iteration += 1
        row.append(iteration)
    return row

def mandelbrot_serial(max_iteration, w, h, xmin, xmax, ymin, ymax):
    start_time = time.time()
    partial_row = partial(mandelbrot_calculate, h=h, w=w, max_iteration=max_iteration, xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax)
    mandelImg = list(map(partial_row, range(h)))
    end_time = time.time()
    print(f"Mode: Serial\tWidth: {w}\tHeight: {h}\tTime: {end_time - start_time:.4f} seconds")
    return mandelImg  

def mandelbrot_parallel(max_iteration, w, h, num_processes, xmin, xmax, ymin, ymax):
    start_time = time.time()
    partial_row = partial(mandelbrot_calculate, h=h, w=w, max_iteration=max_iteration, xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax)
    
    with multiprocessing.Pool(processes=num_processes) as pool:
        mandelImg = pool.map(partial_row, range(h)) 
    end_time = time.time()

    print(f"Mode: Parallel\tWidth: {w}\tHeight: {h}\tNum of processes: {num_processes if num_processes != None else multiprocessing.cpu_count()}\tTime: {end_time - start_time:.4f} seconds")
    return mandelImg

def compute_mandelbrot(max_iter, mode, w, h, processes, xmin, xmax, ymin, ymax):
    if mode == "serial":
        img = mandelbrot_serial(max_iter, w, h, xmin, xmax, ymin, ymax)
    elif mode == "parallel":
        img = mandelbrot_parallel(max_iter, w, h, processes, xmin, xmax, ymin, ymax)
    else:
        print("Invalid mode. Please specify 'serial' or 'parallel'.")
        return
    
    img = np.array(img, dtype=float)  
    img = np.log(img + 1)  
    
    plt.imshow(img, cmap='PuBu', extent=[xmin, xmax, ymin, ymax])
    plt.savefig(f"../data/python/{mode}.png")
    # plt.show()

if __name__ == "__main__":
    start_time = time.time()
    mode = sys.argv[1] if len(sys.argv) > 1 else "serial"
    max_iter = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
    w = int(sys.argv[3]) if len(sys.argv) > 3 else 800
    h = int(sys.argv[4]) if len(sys.argv) > 4 else 500
    xmin = float(sys.argv[5]) if len(sys.argv) > 5 else -2.5
    xmax = float(sys.argv[6]) if len(sys.argv) > 6 else 1.0
    ymin = float(sys.argv[7]) if len(sys.argv) > 7 else -1.0
    ymax = float(sys.argv[8]) if len(sys.argv) > 8 else 1.0

    processes = None
    if mode == "parallel":
        processes = int(sys.argv[9]) if len(sys.argv) > 9 else multiprocessing.cpu_count()
    
    compute_mandelbrot(max_iter, mode, w, h, processes, xmin, xmax, ymin, ymax)
    end_time = time.time()
    print(f"Total execution time: {end_time - start_time:.4f} seconds")
