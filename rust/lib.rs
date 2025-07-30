use std::time::{Duration, Instant};

use ansi::char::AnsiChar;
use pyo3::prelude::*;

mod ansi;
use ansi::drawer::{DrawerFast, Plane};
use ansi::string::AnsiString;
use ansi::{AnsiColor, AnsiGraphics, ColorGround, ColorMode};

#[pyfunction]
fn test_render() -> String {
    let mut drawer = DrawerFast::new(60, 9, None);

    let mut astr_title = AnsiString::new_fore("Rust Drawer", (0, 255, 0));
    astr_title.add_graphics(AnsiGraphics::BOLD | AnsiGraphics::UNDERLINE);

    // place the text on the display
    drawer.text_colored_centered(
        &(AnsiString::new_fore("[ ", (255, 0, 0))
            + astr_title
            + AnsiString::new_fore(" ]", (255, 0, 0))),
        4,
    );

    // render the display
    drawer.render(Some(ColorMode::TRUECOLOR))
}

#[pyfunction]
fn render_benchmark() -> Duration {
    let now = Instant::now();
    for _ in 0..1000000 {
        test_render();
    }
    now.elapsed()
}

/// A Python module implemented in Rust. The name of this function must match
/// the `lib.name` setting in the `Cargo.toml`, else Python will not be able to
/// import the module.
#[pymodule]
fn _drawer(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<DrawerFast>()?;
    m.add_class::<Plane>()?;

    m.add_function(wrap_pyfunction!(test_render, m)?)?;
    m.add_function(wrap_pyfunction!(render_benchmark, m)?)?;

    let color_module = PyModule::new(m.py(), "color")?;
    color_module.add_class::<ColorMode>()?;
    color_module.add_class::<ColorGround>()?;
    color_module.add_class::<AnsiColor>()?;

    m.add_submodule(&color_module)
        .expect("Error on add_submodule! (color)");

    let ansi_module = PyModule::new(m.py(), "ansi")?;
    ansi_module.add_class::<AnsiGraphics>()?;
    ansi_module.add_class::<AnsiChar>()?;
    ansi_module.add_class::<AnsiString>()?;

    m.add_submodule(&ansi_module)
        .expect("Error on add_submodule! (ansi)");

    Ok(())
}
