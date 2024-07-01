import numpy as np
import matplotlib.pyplot as plt

def plot_amdahl(s, p):
    N_values = np.arange(1, 30) 

    amdahl = 1 / (s + p / N_values)
    plt.plot(N_values, amdahl,  linestyle='-', color='b', label='Амдалов закон')


def plot_gaufstason(s, p):
    N_values = np.arange(1, 30) 

    gaufstason = s + p * N_values
    plt.plot(N_values, gaufstason,  linestyle='-', color='r', label='Гауфстафсонов закон')

def rust_strong_scaling():
    real_N = [1, 2, 4, 6, 8, 12, 16, 18]
    serial_time=665.6095
    times = [
        639.638,
        466.853,
        393.328,
        372.541,
        336.99,
        323.165,
        325.128,
        347.788
    ]

    plt.figure(figsize=(10, 6))

    plot_amdahl(0.44, 0.56)

    plt.plot(real_N, serial_time / np.array(times),  'o',  color='r', label='Експериментални подаци')


    plt.title('Јако скалирање')
    plt.xlabel('Број процесора (N)')
    plt.ylabel('Максимум убрзања')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def rust_weak_scaling():
    real_N = [1, 2, 4, 6, 8, 12, 16, 18]

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

    plt.figure(figsize=(10, 6))

    plot_gaufstason(0.44, 0.56)

    plt.plot(real_N, np.array(serial_times) / np.array(times),  'o',  color='r', label='Експериментални подаци')


    plt.title('Слабо скалирање')
    plt.xlabel('Број процесора (N)')
    plt.ylabel('Максимум убрзања')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def python_strong_scaling():
    real_N = [1, 2, 4, 6, 8, 12, 16, 18]
    serial_time=27.1547
    times = [    
        27.1547,
        14.1325,
        9.8518,
        8.5847,
        6.9814,
        6.6512,
        7.5511,
        8.0717
    ]

    plt.figure(figsize=(10, 6))

    plot_amdahl(0.0185, 0.9815)

    plt.plot(real_N, serial_time / np.array(times),  'o',  color='r', label='Експериментални подаци')


    plt.title('Јако скалирање')
    plt.xlabel('Број процесора (N)')
    plt.ylabel('Максимум убрзања')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def python_weak_scaling():
    real_N = [1, 2, 4, 6, 8, 12, 16, 18]

    times = [ 
        2.3403,
        2.2647,
        2.5476,
        2.8089,
        3.6374,
        4.9863,
        6.2200,
        7.446
    ]

    serial_times = [
        2.3403,
        3.4311,
        6.1228,
        8.8029,
        11.2296,
        16.86,
        20.6899,
        22.6349
    ]

    plt.figure(figsize=(10, 6))

    plot_gaufstason(0.44, 0.56)

    plt.plot(real_N, np.array(serial_times) / np.array(times),  'o',  color='r', label='Експериментални подаци')


    plt.title('Слабо скалирање')
    plt.xlabel('Број процесора (N)')
    plt.ylabel('Максимум убрзања')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":

    # rust_strong_scaling()
    # rust_weak_scaling()
    # python_strong_scaling()
    python_weak_scaling()
    
    # n = 1; 27.1547, 1.1559, outliers = 30.2050, 30.1540, 30.0040
    # n = 2; 14.1325, 0.2506
    # n = 4; 9.8518, 0.2726
    # n = 6; 8.5847, 0.4103
    # n = 8; 6.9814, 0.3237
    # n = 12; 6.651233, 0.232344
    # n = 16; 7.5511, 0.3962
    # n = 18;  8.0717, 1.3992, outliers = 15.3950

   
