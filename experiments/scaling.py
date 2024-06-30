import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from python.main import compute_mandelbrot
import time
import multiprocessing
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def plot_scaling(serial_mean, parallel_means, num_processors, title, xlabel, ylabel):
    speedup = [serial_mean / pm for pm in parallel_means]
    ideal_speedup = num_processors

    plt.figure()
    plt.plot(num_processors, speedup, label='Actual Speedup')
    plt.plot(num_processors, ideal_speedup, label='Ideal Speedup', linestyle='--')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.show()

def generate_table(serial_mean, serial_std, serial_times, parallel_means, parallel_stds, parallel_times, num_processors, title):
    data = {
        'Number of Processors': num_processors,
        'Serial Mean Time': [serial_mean] * len(num_processors),
        'Serial Std Dev': [serial_std] * len(num_processors),
        'Parallel Mean Time': parallel_means,
        'Parallel Std Dev': parallel_stds
    }
    df = pd.DataFrame(data)
    print(f"\n{title}\n", df)
    return df


def repeat_measurements(measure_function, max_iter, w, h, mode, processes, repetitions=30):
    times = []
    for _ in range(repetitions):
        time_taken = measure_function(max_iter, w, h, mode, processes)
        times.append(time_taken)
    return np.mean(times), np.std(times), times

def strong_scaling_performance(measure_function, max_iter, w, h, num_processors, repetitions=30):
    serial_mean, serial_std, serial_times = repeat_measurements(measure_function, max_iter, w, h, 'serial', None, repetitions)
    parallel_means = []
    parallel_stds = []
    parallel_times = []
    for p in num_processors:
        mean, std, times = repeat_measurements(measure_function, max_iter, w, h, 'parallel', p, repetitions)
        parallel_means.append(mean)
        parallel_stds.append(std)
        parallel_times.append(times)
    return serial_mean, serial_std, serial_times, parallel_means, parallel_stds, parallel_times


def weak_scaling_performance(measure_function, max_iter, base_w, base_h, num_processors, repetitions=30):
    base_serial_mean, base_serial_std, base_serial_times = repeat_measurements(measure_function, max_iter, base_w, base_h, 'serial', None, repetitions)
    parallel_means = []
    parallel_stds = []
    parallel_times = []
    for p in num_processors:
        w, h = base_w * p, base_h * p
        mean, std, times = repeat_measurements(measure_function, max_iter, w, h, 'parallel', p, repetitions)
        parallel_means.append(mean)
        parallel_stds.append(std)
        parallel_times.append(times)
    return base_serial_mean, base_serial_std, base_serial_times, parallel_means, parallel_stds, parallel_times


def measure_python_performance(max_iter, w, h, mode, processes):
    start_time = time.time()
    compute_mandelbrot(max_iter, mode, w, h, processes)
    end_time = time.time()
    return end_time - start_time


def get_max_speedup():
    max_iter = 100
    w = 800
    h = 500

    serial_time = measure_python_performance(max_iter, w, h, "serial", None)
    
    processes = multiprocessing.cpu_count()

    parallel_time = measure_python_performance(max_iter, w, h, "parallel", processes)

    print(f"Sequential execution time: {serial_time:.4f} S")
    print(f"Parallel execution time with {processes} processors: {parallel_time:.4f} S")

    S = (parallel_time - (serial_time / processes)) / parallel_time
    P = 1 - S

    print(f"Sequential code percent: {S:.4f}")
    print(f"Parallel code percent: {P:.4f}")
   
    Amdal_max_speedup = 1 / (S + (P / processes))
    Gustafson_max_speedup = S + (P * processes)

    print(f"Amdahl's law: {Amdal_max_speedup:.4f}")
    print(f"Gustafson's law: {Gustafson_max_speedup:.4f}")


if __name__ == "__main__":

    s = 0.44  
    p = 0.56  

    N_values = np.arange(1, 30) 

    amdahl = 1 / (s + p / N_values)
    gaufstason = s + p * N_values

    plt.figure(figsize=(10, 6))
    # plt.plot(N_values, amdahl,  linestyle='-', color='b', label='Амдалов закон')
    plt.plot(N_values, gaufstason,  linestyle='-', color='r', label='Гауфстафсонов закон')

    real_N = [1, 2, 4, 6, 8, 12, 16, 18]
    # serial_time=665.6095
    # times = [
    #     639.638,
    #     466.853,
    #     393.328,
    #     372.541,
    #     336.99,
    #     323.165,
    #     325.128,
    #     347.788
    # ]

    times = [ 
        0.6325,
        0.9164,
        1.5516,
        2.0921,
        2.6565,
        3.8464,
        5.0901,
        6.9013
    ]

    serial_times = [
        0.66561,
        1.3786,
        2.8698,
        4.10068,
        5.48921,
        8.467371,
        11.45148,
        14.59848
    ]

    
    plt.plot(real_N, np.array(serial_times) / np.array(times),  'o',  color='r', label='Експериментални подаци')

    plt.title('Слабо скалирање')
    plt.xlabel('Број процесора (N)')
    plt.ylabel('Максимум убрзања')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


    # get_max_speedup()
    
    # max_iter = 100
    # w = 800
    # h = 500
    # base_w = 200
    # base_h = 125
    # num_processors = [1, 2, 4, 8, 12, None]
    # repetitions = 10

    # # Jako skaliranje Python
    # serial_mean, serial_std, serial_times, parallel_means, parallel_stds, parallel_times = strong_scaling_performance(measure_python_performance, max_iter, w, h, num_processors, repetitions)
    # plot_scaling(serial_mean, parallel_means, num_processors, 'Jako skaliranje Python', 'Broj procesora', 'Ubrzanje')
    # generate_table(serial_mean, serial_std, serial_times, parallel_means, parallel_stds, parallel_times, num_processors, 'Tabela: Jako skaliranje Python')

    # Jako skaliranje Rust
    # serial_mean, serial_std, serial_times, parallel_means, parallel_stds, parallel_times = strong_scaling_performance(measure_rust_performance, max_iter, w, h, num_processors, repetitions)
    # plot_scaling(serial_mean, parallel_means, num_processors, 'Jako skaliranje Rust', 'Broj procesora', 'Ubrzanje')
    # generate_table(serial_mean, serial_std, serial_times, parallel_means, parallel_stds, parallel_times, num_processors, 'Tabela: Jako skaliranje Rust')

    # Slabo skaliranje Python
    # serial_mean, serial_std, serial_times, parallel_means, parallel_stds, parallel_times = weak_scaling_performance(measure_python_performance, max_iter, base_w, base_h, num_processors, repetitions)
    # plot_scaling(serial_mean, parallel_means, num_processors, 'Slabo skaliranje Python', 'Broj procesora', 'Ubrzanje')
    # generate_table(serial_mean, serial_std, serial_times, parallel_means, parallel_stds, parallel_times, num_processors, 'Tabela: Slabo skaliranje Python')

    # Slabo skaliranje Rust
    # serial_mean, serial_std, serial_times, parallel_means, parallel_stds, parallel_times = weak_scaling_performance(measure_rust_performance, max_iter, base_w, base_h, num_processors, repetitions)
    # plot_scaling(serial_mean, parallel_means, num_processors, 'Slabo skaliranje Rust', 'Broj procesora', 'Ubrzanje')
    # generate_table(serial_mean, serial_std, serial_times, parallel_means, parallel_stds, parallel_times, num_processors, 'Tabela: Slabo skaliranje Rust')

    # for i in range(10):
    #     compute_mandelbrot(1000, 'serial', 800, 500, None, -2.5, 1.0, -1.0, 1.0)
    # 25.770