use eframe::egui::{self, CentralPanel, TopBottomPanel};
use egui_plotter::EguiBackend;
use plotters::prelude::*;
use rayon::prelude::*;
use std::env;
use std::ops::Range;
use std::time::Instant;

fn main() {
    let start_time = Instant::now();
    let args: Vec<String> = env::args().collect();
    let mode = if args.len() > 1 { &args[1] } else { "serial" };

    if mode.eq("strong_scale") {
        strong_scale();
        return;
    }else if mode.eq("weak_scale") {
        weak_scale();
        return;
    }

    let max_iter = if args.len() > 2 {
        args[2].parse::<usize>().unwrap_or(1000)
    } else {
        1000
    };

    let w = if args.len() > 3 {
        args[3].parse::<u32>().unwrap_or(800)
    } else {
        800
    };

    let h = if args.len() > 4 {
        args[4].parse::<u32>().unwrap_or(600)
    } else {
        500
    };

    let xmin = if args.len() > 5 {
        args[5].parse::<f64>().unwrap_or(-2.2)
    } else {
        -2.5
    };

    let xmax = if args.len() > 6 {
        args[6].parse::<f64>().unwrap_or(1.0)
    } else {
        1.0
    };

    let ymin = if args.len() > 7 {
        args[7].parse::<f64>().unwrap_or(-1.2)
    } else {
        -1.0
    };

    let ymax = if args.len() > 8 {
        args[8].parse::<f64>().unwrap_or(1.2)
    } else {
        1.0
    };

    let processes: Option<usize> = if args.len() > 9 {
        args[9].parse::<usize>().ok()
    } else {
        None
    };

    if mode.eq("gui") {
        rayon::ThreadPoolBuilder::new()
            .num_threads(num_cpus::get())
            .build_global()
            .unwrap();

        // Create and run the application
        let app = MandelbrotApp::default();
        let native_options = eframe::NativeOptions::default();
        let _ = eframe::run_native(
            "Mandelbrot Viewer",
            native_options,
            Box::new(|_cc| Box::new(app)),
        );
    } else {
        let num_threads = processes.unwrap_or_else(|| num_cpus::get());
        if mode.eq("parallel") {
            rayon::ThreadPoolBuilder::new()
                .num_threads(num_threads)
                .build_global()
                .unwrap();
        }
        let _ = compute_mandelbrot(max_iter, mode, w, h, num_threads, xmin, xmax, ymin, ymax);
    }

    let end_time = Instant::now();
    let elapsed_time = end_time - start_time;
    println!("Total execution time: {:?}", elapsed_time);
}

fn compute_mandelbrot(
    max_iter: usize,
    mode: &str,
    w: u32,
    h: u32,
    processes: usize,
    xmin: f64,
    xmax: f64,
    ymin: f64,
    ymax: f64,
) -> Result<(), Box<dyn std::error::Error>> {
    let path = format!("../data/rust/{}.png", mode);
    let root = BitMapBackend::new(&path, (w, h)).into_drawing_area();
    root.fill(&WHITE)?;

    let mut chart = ChartBuilder::on(&root)
        .margin(20)
        .x_label_area_size(10)
        .y_label_area_size(10)
        .build_cartesian_2d(xmin..xmax, ymin..ymax)?;

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
            let start_time = Instant::now();
            let set = mandelbrot_set(xr, yr, (pw as usize, ph as usize), max_iter);
            let end_time = Instant::now();
            let elapsed_time = end_time - start_time;
            println!(
                "Mode: {}\tWidth: {}\tHeight: {}\tTime: {:?}",
                mode, w, h, elapsed_time
            );
            for (x, y, c) in set {
                if c != max_iter {
                    plotting_area.draw_pixel((x, y), &color_from_iteration(c, max_iter))?;
                } else {
                    plotting_area.draw_pixel((x, y), &BLACK)?;
                }
            }
        }
        "parallel" => {
            let start_time = Instant::now();
            let set = mandelbrot_set_parallel(xr, yr, (pw as usize, ph as usize), max_iter);
            let end_time = Instant::now();
            let elapsed_time = end_time - start_time;
            println!(
                "Mode: {}\tWidth: {}\tHeight: {}\tNum of threads: {}\tTime: {:?}",
                mode, w, h, processes, elapsed_time
            );
            for (x, y, c) in set {
                if c != max_iter {
                    plotting_area.draw_pixel((x, y), &color_from_iteration(c, max_iter))?;
                } else {
                    plotting_area.draw_pixel((x, y), &BLACK)?;
                }
            }
        }
        _ => {
            println!("Invalid mode. Please specify one of: 'serial', 'parallel', 'gui', 'strong_scale', 'weak_scale'.");
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
) -> Vec<(f64, f64, usize)> {
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
) -> Vec<(f64, f64, usize)> {
    let step = (
        (real.end - real.start) / samples.0 as f64,
        (complex.end - complex.start) / samples.1 as f64,
    );
    (0..(samples.0 * samples.1))
        .map(move |k| {
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

fn color_from_iteration(iteration: usize, max_iter: usize) -> RGBColor {
    if iteration == max_iter {
        return RGBColor(0, 0, 0);
    }

    let t = iteration as f64 / max_iter as f64;
    let r = (9.0 * (1.0 - t) * t * t * t * 255.0) as u8;
    let g = (15.0 * (1.0 - t) * (1.0 - t) * t * t * 255.0) as u8;
    let b = (8.5 * (1.0 - t) * (1.0 - t) * (1.0 - t) * t * 255.0) as u8;

    RGBColor(r, g, b)
}

////

struct MandelbrotApp {
    max_iter: usize,
    width: u32,
    height: u32,
    xmin: f64,
    xmax: f64,
    ymin: f64,
    ymax: f64,
}

impl Default for MandelbrotApp {
    fn default() -> Self {
        Self {
            max_iter: 1000,
            width: 800,
            height: 500,
            xmin: -2.5,
            xmax: 1.0,
            ymin: -1.0,
            ymax: 1.0,
        }
    }
}

impl eframe::App for MandelbrotApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        TopBottomPanel::top("top_panel").show(ctx, |ui| {
            ui.horizontal(|ui| {
                ui.label("Max Iterations:");
                ui.add(egui::Slider::new(&mut self.max_iter, 10..=5000));
            });
            ui.horizontal(|ui| {
                if ui
                    .button("Snapshot")
                    .on_hover_text("Take a snapshot of the current view")
                    .clicked()
                {
                    let res = take_snapshot(self);
                    if let Err(_e) = res {
                        // eprintln!("Error: {:?}", e);
                    }
                };
            });
        });

        CentralPanel::default().show(ctx, |ui| {
            let response = ui.allocate_rect(ui.max_rect(), egui::Sense::drag());
            if response.dragged() {
                let delta = response.drag_delta();
                let scale_x = (self.xmax - self.xmin) / self.width as f64;
                let scale_y = (self.ymax - self.ymin) / self.height as f64;
                self.xmin -= delta.x as f64 * scale_x;
                self.xmax -= delta.x as f64 * scale_x;
                self.ymin += delta.y as f64 * scale_y;
                self.ymax += delta.y as f64 * scale_y;
            }

            let zoom_delta: f32 = response.ctx.input(|i| i.zoom_delta()).into();
            let zoom_factor: f32 = 2.0;
            let (center_x, center_y) =
                ((self.xmax + self.xmin) / 2.0, (self.ymax + self.ymin) / 2.0);

            if zoom_delta > 1.0 {
                // Zoom in
                let factor: f64 = zoom_factor.powf(zoom_delta - 1.0).into();
                self.xmin = center_x + (self.xmin - center_x) / factor;
                self.xmax = center_x + (self.xmax - center_x) / factor;
                self.ymin = center_y + (self.ymin - center_y) / factor;
                self.ymax = center_y + (self.ymax - center_y) / factor;
            } else if zoom_delta < 1.0 {
                // Zoom out
                let factor: f64 = zoom_factor.powf(1.0 - zoom_delta).into();
                self.xmin = center_x + (self.xmin - center_x) * factor;
                self.xmax = center_x + (self.xmax - center_x) * factor;
                self.ymin = center_y + (self.ymin - center_y) * factor;
                self.ymax = center_y + (self.ymax - center_y) * factor;
            }

            draw_mandelbrot(self, EguiBackend::new(ui))
        });
        ctx.request_repaint();
    }
}

fn draw_mandelbrot<D: DrawingBackend>(
    app: &MandelbrotApp,
    backend: D,
) -> Result<(), Box<dyn std::error::Error + 'static>>
where
    D::ErrorType: 'static,
{
    let root = backend.into_drawing_area();
    root.fill(&WHITE)?;

    let mut chart = ChartBuilder::on(&root)
        .margin(20)
        .x_label_area_size(10)
        .y_label_area_size(10)
        .build_cartesian_2d(app.xmin..app.xmax, app.ymin..app.ymax)?;

    chart
        .configure_mesh()
        .disable_x_mesh()
        .disable_y_mesh()
        .draw()?;

    let plotting_area = chart.plotting_area();
    let range = plotting_area.get_pixel_range();
    let (pw, ph) = (range.0.end - range.0.start, range.1.end - range.1.start);
    let (xr, yr) = (chart.x_range(), chart.y_range());

    let set = mandelbrot_set_parallel(xr, yr, (pw as usize, ph as usize), app.max_iter);

    for (x, y, c) in set {
        if c != app.max_iter {
            plotting_area.draw_pixel((x, y), &color_from_iteration(c, app.max_iter))?;
        } else {
            plotting_area.draw_pixel((x, y), &BLACK)?;
        }
    }
    root.present()?;
    Ok(())
}

fn take_snapshot(app: &MandelbrotApp) -> Result<(), Box<dyn std::error::Error>> {
    let path = format!("../data/rust/{}.png", "gui");

    draw_mandelbrot(app, BitMapBackend::new(&path, (app.width, app.height)))
}

fn calculate_mean(data: &[f64]) -> f64 {
    let sum: f64 = data.iter().sum();
    sum / data.len() as f64
}

fn calculate_variance(data: &[f64], mean: f64) -> f64 {
    let variance: f64 = data
        .iter()
        .map(|value| {
            let diff = mean - *value;
            diff * diff
        })
        .sum();
    variance / data.len() as f64
}

fn calculate_standard_deviation(data: &[f64]) -> f64 {
    let mean = calculate_mean(data);
    let variance = calculate_variance(data, mean);
    variance.sqrt()
}

fn strong_scale() {
    let processes = [1, 2, 4, 6, 8, 12, 16, 18];
    let max_iter = 1000;
    let w = 800;
    let h = 500;
    let xmin = -2.5;
    let xmax = 1.0;
    let ymin = -1.0;
    let ymax = 1.0;

    for &p in processes.iter() {
        let pool = rayon::ThreadPoolBuilder::new()
            .num_threads(p)
            .build()
            .unwrap();

        pool.scope(|_| {
            let mut vec = Vec::<std::time::Duration>::new();
            for _ in 0..30 {
                let start_time = Instant::now();
                let _ = compute_mandelbrot(max_iter, "parallel", w, h, p, xmin, xmax, ymin, ymax);
                let end_time = Instant::now();
                let elapsed_time = end_time - start_time;
                vec.push(elapsed_time);
                // println!("Processes: {}\tTime: {:?}", p, elapsed_time);
            }

            let times: Vec<f64> = vec.iter().map(|d| d.as_secs_f64()).collect();
            println!(
                "Processes: {}\tMean time: {:?}\tStd dev: {:?}",
                p,
                calculate_mean(&times),
                calculate_standard_deviation(&times)
            );
        });
    }
}


fn weak_scale(){
    let processes = [1, 2, 4, 6, 8, 12, 16, 18];
    let max_iter = 1000;
    let w = 800;
    let h = [500, 1000, 2000, 3000, 4000, 6000, 8000, 10000];
    let xmin = -2.5;
    let xmax = 1.0;
    let ymin = -1.0;
    let ymax = 1.0;


    for i in 0..8{
        let height = h[i];
        let pool = rayon::ThreadPoolBuilder::new()
            .num_threads(processes[i])
            .build()
            .unwrap();

        pool.scope(|_| {
            let mut vec = Vec::<std::time::Duration>::new();
            for _ in 0..30 {
                let start_time = Instant::now();
                let _ = compute_mandelbrot(max_iter, "parallel", w, height, processes[i], xmin, xmax, ymin, ymax);
                let end_time = Instant::now();
                let elapsed_time = end_time - start_time;
                vec.push(elapsed_time);
                // println!("Processes: {}\tTime: {:?}", p, elapsed_time);
            }

            let times: Vec<f64> = vec.iter().map(|d| d.as_secs_f64()).collect();
            println!(
                "Processes: {}\tMean time: {:?}\tStd dev: {:?}",
                processes[i],
                calculate_mean(&times),
                calculate_standard_deviation(&times)
            );
        });
    }
}
