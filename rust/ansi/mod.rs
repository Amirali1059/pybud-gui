#![allow(unused)]
use pyo3::prelude::*;

pub mod char;
pub mod string;
pub mod drawer;

// Types
#[pyclass]
#[derive(Clone, Copy)]
pub struct AnsiColor(pub u8, pub u8, pub u8);

impl PartialEq for AnsiColor {
    fn eq(&self, other: &Self) -> bool {
        (self.0 == other.0) && (self.1 == other.1) && (self.2 == other.2)
    }
}

fn calc_legacy_colorbit(c: u8) -> u8{
    /* 
    legacy color usually ranges from about 48 to 236, 
    this function translates a single color to legacy base 6
    */

    const K: f32 = 5.0 / 187.0; // constant ratio
    
    if c >= 48 {
        ((c-48) as f32 * K) as u8
    } else {
        0
    }
}

#[pymethods]
impl AnsiColor {
    #[new]
    fn new(r: u8, g: u8, b: u8) -> Self{
        AnsiColor {0: r, 1: g, 2:b}
    }

    fn truecolor_render(&self, ground: &ColorGround) -> String {
        let cmd = match ground {
            ColorGround::Back => "48",
            ColorGround::Fore => "38",
        };
        format!("\x1b[{};2;{};{};{}m", cmd, self.0, self.1, self.2)
    }

    fn limited_render(&self, ground: &ColorGround) -> String {
        let cmd = match ground {
            ColorGround::Back => "48",
            ColorGround::Fore => "38",
        };
        let r = calc_legacy_colorbit(self.0);
        let g = calc_legacy_colorbit(self.1);
        let b = calc_legacy_colorbit(self.2);
        let color_code = r * 36 + g * 6 + b + 16;

        format!("\x1b[{};5;{}m", cmd, color_code)
    }

    pub fn to_string(&self, mode: &ColorMode, ground: &ColorGround) -> String {
        match mode {
            ColorMode::TrueColor => self.truecolor_render(ground),
            ColorMode::Limited => self.limited_render(ground)
        }
    }
}

#[pyclass]
#[derive(Clone, Copy)]
pub enum ColorGround {
    Back,
    Fore
}
#[pyclass]
#[derive(Clone, Copy)]
pub enum ColorMode {
    Limited,
    TrueColor
}

const ANSIRESET: &str = "\x1b[0m";
const RESET_FOREGROUND: &str = "\x1b[0;39m";
const RESET_BACKGROUND: &str = "\x1b[0;49m";

#[pyclass]
#[derive(Clone, Copy)]
#[derive(PartialEq)]
pub enum AnsiGraphicMode {
    Bold      = 0,
    Faint     = 1,
    Italic    = 2,
    Underline = 3,
    Blinking  = 4,
//  Undefined = 5,
    Reverse   = 6,
    Hidden    = 7,
    Strike    = 8,
}

#[pyclass]
#[derive(Clone)]
pub struct AnsiGraphics {
    #[pyo3(get, set)]
    pub modes: Vec<AnsiGraphicMode>
}

#[pymethods]
impl AnsiGraphics {
    const MAP: [(&'static str, &'static str); 9] = [
        // set    ,    reset  
        ("\x1b[1m", "\x1b[22m"), // 0 -> bold
        ("\x1b[2m", "\x1b[22m"), // 1 -> faint
        ("\x1b[3m", "\x1b[23m"), // 2 -> italic
        ("\x1b[4m", "\x1b[24m"), // 3 -> underline
        ("\x1b[5m", "\x1b[25m"), // 4 -> blinking
        ("", "")               , // 5 -> UNDEFINED
        ("\x1b[7m", "\x1b[27m"), // 6 -> reverse
        ("\x1b[8m", "\x1b[28m"), // 7 -> hidden
        ("\x1b[9m", "\x1b[29m"), // 8 -> strike
        ];
    
    #[staticmethod]
    #[inline]
    pub fn get_mode(mode: AnsiGraphicMode, reset: bool) -> &'static str {
        let idx = mode as usize;
        let mode = match Self::MAP.get(idx) {
            None => {("", "")},
            Some(t) => {t.clone()}
        };

        match reset {
            false => {mode.0},
            true => {mode.1}
        }
    }

    pub fn to_string(&self, reset: bool) -> String {
        let mut result = String::new();

        for mode in self.modes.clone() {
            result.push_str(Self::get_mode(mode, reset))
        }

        result
    }

    // python __str__ magic function
    pub fn __str__(&self) -> String {
        self.to_string(false)
    }

    // TODO: optimize, this is 2o(n*m)
    pub fn is_eq(&self, other: &Self) -> bool {
        if self.modes.len() != other.modes.len() {
            return false;
        }

        // loop into all self.modes
        for agm in self.modes.clone() {
            // if other.modes does not contain one of the agms, return false
            if !other.modes.contains(&agm) {
                return false;
            }
        }

        // loop into all other.modes
        for agm in other.modes.clone() {
            // if self.modes does not contain one of the agms, return false
            if !self.modes.contains(&agm) {
                return false;
            }
        }

        // if no inequalities are found return true
        true
    }

    pub fn add(&mut self, agm: AnsiGraphicMode) {
        if !self.modes.contains(&agm){
            self.modes.push(agm);
        }
    }

    // python operation add
    pub fn __add__(&mut self, agm: AnsiGraphicMode) -> Self{
        let mut r = self.clone();
        r.add(agm);
        
        r
    }

    #[new]
    fn new() -> Self{
        AnsiGraphics {modes: Vec::new()}
    }

}