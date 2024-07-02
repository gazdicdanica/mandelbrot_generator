# Mandelbrot Generator
- 10

## Definition
The Mandelbrot set is a two-dimensional set with a definition that exhibits great complexity, especially when magnified. It has its origin in complex dynamics

The set is defined in the complex plane as the complex numbers $c$ for which the function $f_{c}(z)=z^{2}+c$ does not diverge to infinity when iterated starting at $z=0$, i.e., for which the sequence $f_{c}(0)$, $f_{c}(f_{c}(0))$, etc., remains bounded in absolute value.


<img src="https://github.com/gazdicdanica/mandelbrot_generator/blob/main/data/rust/parallel.png" width=800 alt="default mandelbrot image">

<img src="https://github.com/gazdicdanica/mandelbrot_generator/blob/main/data/rust/serial.png" width=800 alt="mandelbrot image and different position">  



## Solution
The solution will be implemented in Python and Rust, sequential and parallelised, as well as visualization of the final result


## How to start
- Clone the git project

### Rust
- [Install Rust](https://www.rust-lang.org/tools/install)
- Position yourself in ./rust subfolder
- Run with command:
  ```
  cargo run {mode} {max_iter} {w} {h} {x_min} {x_max} {y_min} {y_max} {num_of_processes}
  ```
- All arguments are optional and have [default values](#command-line-arguments)
- parallel and serial mode produce results in data/rust/{mode}.png

### Python
- [Install Python](https://www.python.org/downloads/)
- Position yourself in ./python subfolder
- To install dependencies, run:
  ```
  pip install -r requirements.txt
  ```
- Run with command
  ```
  python main.py {mode} {max_iter} {w} {h} {x_min} {x_max} {y_min} {y_max} {num_of_processes}
  ```
- All arguments are optional and have [default values](#command-line-arguments)
- parallel and serial mode produce results in data/python/{mode}.png



## Command line arguments
- mode = ['parallel', 'serial', 'gui' *(only in Rust implementation)*, 'strong_scale', 'weak_scale'] (default = 'serial')
- max_iter = num of iteration for computing the set (default = 1000)
- w = width of img to compute (default = 800)
- h = height of img to compute (default = 500)
- x_min, x_max, y_min, y_max = marginal positions (default = [-2.5, 1.0, -1.0, 1.0])
    - other values I recommend
      - [-0.776606, -0.776581, -0.136651, -0.136630],
      - [-1.7687782, -1.7687794, -0.0017384, -0.0017394]   
- num_of_processes = number of threads to be created while running the parallel version (default = num. of cores on your machine) *only applicable when running with mode='parallel'*
