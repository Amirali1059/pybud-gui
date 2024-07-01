use pyo3::prelude::*;
use bitflags::bitflags;

pub mod char;
pub mod string;
pub mod drawer;

// Types
#[pyclass]
#[derive(Clone, Copy, PartialEq)]
pub struct AnsiColor(pub u8, pub u8, pub u8);

fn calc_legacy_color(c: u8) -> u8 {
    /* 
    legacy colors have an estimated range from about 48 to 236, 
    this function translates a single color to legacy base 6
    */

    // const K: f32 = 5.0 / 187.0; // constant ratio
    
    if c >= 48 { ((c - 48) * 5) / 187 } else { 0 }
}

impl AnsiColor {
    #[inline]
    fn get_ground_code(ground: &ColorGround) -> &str {
        match ground {
            ColorGround::BACK => "48",
            ColorGround::FORE => "38",
        }
    }

    fn truecolor_render(&self, ground: &ColorGround) -> String {
        format!("\x1b[{};2;{};{};{}m", Self::get_ground_code(ground), self.0, self.1, self.2)
    }

    fn limited_render(&self, ground: &ColorGround) -> String {
        
        let r = calc_legacy_color(self.0);
        let g = calc_legacy_color(self.1);
        let b = calc_legacy_color(self.2);
        let color_code = r * 36 + g * 6 + b + 16;

        format!("\x1b[{};5;{}m", Self::get_ground_code(ground), color_code)
    }
}

#[pymethods]
impl AnsiColor {
    #[new]
    fn new(r: u8, g: u8, b: u8) -> Self {
        Self {0: r, 1: g, 2:b}
    }

    pub fn to_string(&self, mode: &ColorMode, ground: &ColorGround) -> String {
        match mode {
            ColorMode::TRUECOLOR => self.truecolor_render(ground),
            ColorMode::LIMITED => self.limited_render(ground)
        }
    }

    // python __eq__ magic function
    pub fn __eq__(&self, other: &Self) -> bool {
        self == other
    }
}

#[pyclass]
#[derive(Clone, Copy)]
pub enum ColorGround {
    BACK,
    FORE
}
#[pyclass]
#[derive(Clone, Copy)]
pub enum ColorMode {
    LIMITED,
    TRUECOLOR
}

const ANSIRESET: &str = "\x1b[0m";
//const RESET_FOREGROUND: &str = "\x1b[0;39m";
//const RESET_BACKGROUND: &str = "\x1b[0;49m";

bitflags! {
    #[pyclass]
    #[derive(Clone, Copy, PartialEq)]
    pub struct AnsiGraphics: u8 {
        const BOLD      = 0b00000001;
        const FAINT     = 0b00000010;
        const ITALIC    = 0b00000100;
        const UNDERLINE = 0b00001000;
        const BLINKING  = 0b00010000;
        const REVERSE   = 0b00100000;
        const HIDDEN    = 0b01000000;
        const STRIKE    = 0b10000000;
    }
}

impl AnsiGraphics {
    const IDX2ANSI: [(&'static str, &'static str); 8] = [
        // set    ,    reset  
        ("\x1b[1m", "\x1b[22m"), // 0 -> BOLD
        ("\x1b[2m", "\x1b[22m"), // 1 -> FAINT
        ("\x1b[3m", "\x1b[23m"), // 2 -> ITALIC
        ("\x1b[4m", "\x1b[24m"), // 3 -> UNDERLINE
        ("\x1b[5m", "\x1b[25m"), // 4 -> BLINKING
        ("\x1b[7m", "\x1b[27m"), // 5 -> REVERSE
        ("\x1b[8m", "\x1b[28m"), // 6 -> HIDDEN
        ("\x1b[9m", "\x1b[29m"), // 7 -> STRIKE
        ];
    
    const NAME2IDX: [(&'static str, u8); 8] = [
        // set    ,    reset  
        ("BOLD", 0), 
        ("FAINT", 1), 
        ("ITALIC", 2), 
        ("UNDERLINE", 3), 
        ("BLINKING", 4),
        ("REVERSE", 5),
        ("HIDDEN", 6),
        ("STRIKE", 7),
        ];

    #[inline]
    pub fn get_mode(name: &str, reset: bool) -> &'static str {
        let mut i: usize = 0;
        let idx = loop {
            if i < Self::NAME2IDX.len(){
                let mapping = Self::NAME2IDX[i];
                if mapping.0 == name.to_uppercase() {
                    break mapping.1 as i8
                }
                i += 1;
            } else {
                break -1
            }
        };

        if idx == -1{
            print!("Could not find mode with name \"{}\".", name);
            panic!()
        }

        let idx: usize = idx as usize;

        let graphic_ansi_codes = match Self::IDX2ANSI.get(idx) {
            None => {("", "")},
            Some(t) => {*t}
        };

        match reset {
            false => {graphic_ansi_codes.0},
            true => {graphic_ansi_codes.1}
        }
    }
}

#[pymethods]
impl AnsiGraphics {
    #[new]
    #[inline]
    fn new() -> Self {
        Self::empty()
    }

    #[staticmethod]
    #[inline]
    fn _from_bits(bits: u8) -> Option<Self> {
        Self::from_bits(bits)
    }

    pub fn to_string(&self, reset: bool) -> String {
        let mut result = String::new();

        for mode in self.iter_names() {
            result.push_str(Self::get_mode(mode.0, reset))
        }

        result
    }

    // python __str__ magic function
    pub fn __str__(&self) -> String {
        self.to_string(false)
    }

    // python __eq__ magic function
    pub fn __eq__(&self, other: &Self) -> bool {
        self == other
    }

    // python __or__ magic function
    pub fn __or__(&self, other: &Self) -> Self {
        *self | *other
    }
}