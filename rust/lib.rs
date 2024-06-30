#![allow(unused)]
use ansi::char::AnsiChar;
use pyo3::prelude::*;

mod ansi;
use ansi::{AnsiColor, AnsiGraphicMode, AnsiGraphics, ColorGround, ColorMode};
use ansi::drawer::Drawer;
use ansi::string::AnsiString;

#[pyfunction]
fn test_render() -> String {
    let mut drawer = Drawer::new((9, 60), None);
    
    let mut astr_title = AnsiString::new_fore( "Rust Drawer", Some((0, 255, 0)));
    astr_title.add_graphics(AnsiGraphicMode::Italic);
    astr_title.add_graphics(AnsiGraphicMode::Underline);
    
    let mut astr_title_bracets = AnsiString::new_fore("[             ]", Some((255, 0, 0)));
    astr_title_bracets.center_place(&astr_title, false);

    // place the text on the display
    drawer.center_place(&astr_title_bracets, 4, false);

    // render the display
    drawer.render(&ColorMode::TrueColor)
}


/// A Python module implemented in Rust. The name of this function must match
/// the `lib.name` setting in the `Cargo.toml`, else Python will not be able to
/// import the module.
#[pymodule]
fn _drawer(m: &Bound<'_, PyModule>) -> PyResult<()> {

    m.add_function(wrap_pyfunction!(test_render, m)?)?;

    let color_module = PyModule::new_bound(m.py(), "color")?;
    color_module.add_class::<ColorMode>()?;
    color_module.add_class::<ColorGround>()?;
    color_module.add_class::<AnsiColor>()?;

    let ansi_module = PyModule::new_bound(m.py(), "ansi")?;
    ansi_module.add_class::<AnsiGraphicMode>()?;
    ansi_module.add_class::<AnsiGraphics>()?;
    ansi_module.add_class::<AnsiChar>()?;
    ansi_module.add_class::<AnsiString>()?;

    m.add_class::<Drawer>()?;
    m.add_submodule(&ansi_module);
    m.add_submodule(&color_module);

    Ok(())
}