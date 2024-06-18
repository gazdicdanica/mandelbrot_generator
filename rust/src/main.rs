use plotters::prelude::*;
use rayon::prelude::*;
use std::env;
use std::ops::Range;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = env::args().collect();
    let mode = if args.len() > 1 { &args[1] } else { "serial" };

    let max_iter = if args.len() > 2 {
        args[2].parse::<usize>().unwrap_or(100)
    } else { 100 };

    let w = if args.len() > 3 {
        args[3].parse::<u32>().unwrap_or(800)
    } else { 800 };
    
    let h = if args.len() > 4 {
        args[4].parse::<u32>().unwrap_or(600)
    } else { 600 };

    let processes : Option<usize> = if args.len() > 5 {
        args[5].parse::<usize>().ok()
    } else { None };

    compute_mandelbrot(max_iter, mode, w, h, processes)
}

fn compute_mandelbrot(max_iter: usize, mode: &str, w: u32, h: u32, processes: Option<usize>) -> Result<(), Box<dyn std::error::Error>> {
    let path = format!("../data/rust/{}.png", mode);
    let root = BitMapBackend::new(&path, (w, h)).into_drawing_area();
    root.fill(&WHITE)?;

    let mut chart = ChartBuilder::on(&root)
        .margin(20)
        .x_label_area_size(10)
        .y_label_area_size(10)
        .build_cartesian_2d(-2.1f64..0.6f64, -1.2f64..1.2f64)?;

    chart
        .configure_mesh()
        .disable_x_mesh()
        .disable_y_mesh()
        .draw()?;

    let plotting_area = chart.plotting_area();
    let range = plotting_area.get_pixel_range();
    let (pw, ph) = (range.0.end - range.0.start, range.1.end - range.1.start);
    let (xr, yr) = (chart.x_range(), chart.y_range());

    match mode {
        "serial" => {
            for (x, y, c) in mandelbrot_set(xr, yr, (pw as usize, ph as usize), max_iter) {
                if c != max_iter {
                    plotting_area.draw_pixel(
                        (x, y),
                        &MandelbrotHSL::get_color(c as f64 / max_iter as f64),
                    )?;
                } else {
                    plotting_area.draw_pixel((x, y), &BLACK)?;
                }
            }
        }
        "parallel" => {
            for (x, y, c) in mandelbrot_set_parallel(xr, yr, (pw as usize, ph as usize), max_iter, processes) {
                if c != max_iter {
                    plotting_area.draw_pixel(
                        (x, y),
                        &MandelbrotHSL::get_color(c as f64 / max_iter as f64),
                    )?;
                } else {
                    plotting_area.draw_pixel((x, y), &BLACK)?;
                }
            }
        }
        _ => {
            println!("Invalid mode. Please specify 'serial' or 'parallel'.");
            return Ok(());
        }
    }

    root.present()?;
    Ok(())
}

fn mandelbrot_set_parallel(
    real: Range<f64>,
    complex: Range<f64>,
    samples: (usize, usize),
    max_iter: usize,
    num_processes: Option<usize>,
) -> Vec<(f64, f64, usize)> {
    let num_threads = num_processes.unwrap_or_else(|| num_cpus::get());
    rayon::ThreadPoolBuilder::new()
        .num_threads(num_threads)
        .build_global()
        .unwrap();

    let step = (
        (real.end - real.start) / samples.0 as f64,
        (complex.end - complex.start) / samples.1 as f64,
    );

    (0..(samples.0 * samples.1))
    .into_par_iter()
    .map(|k| {
        let c = (
            real.start + step.0 * (k % samples.0) as f64,
            complex.start + step.1 * (k / samples.0) as f64,
        );
        let mut z = (0.0, 0.0);
        let mut cnt = 0;
        while cnt < max_iter && z.0 * z.0 + z.1 * z.1 <= 1e10 {
            z = (z.0 * z.0 - z.1 * z.1 + c.0, 2.0 * z.0 * z.1 + c.1);
            cnt += 1;
        }
        (c.0, c.1, cnt)
    })
    .collect()
}

fn mandelbrot_set(
    real: Range<f64>,
    complex: Range<f64>,
    samples: (usize, usize),
    max_iter: usize,
) -> impl Iterator<Item = (f64, f64, usize)> {
    let step = (
        (real.end - real.start) / samples.0 as f64,
        (complex.end - complex.start) / samples.1 as f64,
    );
    (0..(samples.0 * samples.1)).map(move |k| {
        let c = (
            real.start + step.0 * (k % samples.0) as f64,
            complex.start + step.1 * (k / samples.0) as f64,
        );
        let mut z = (0.0, 0.0);
        let mut cnt = 0;
        while cnt < max_iter && z.0 * z.0 + z.1 * z.1 <= 1e10 {
            z = (z.0 * z.0 - z.1 * z.1 + c.0, 2.0 * z.0 * z.1 + c.1);
            cnt += 1;
        }
        (c.0, c.1, cnt)
    })
}
