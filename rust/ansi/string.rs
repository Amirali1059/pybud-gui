use pyo3::prelude::*;

use std::ops::Add;

use crate::ansi::{AnsiColor, AnsiGraphics, ANSIRESET};

use super::char::AnsiChar;
use super::{ColorGround, ColorMode};

#[pyclass]
#[derive(Clone, PartialEq)]
pub struct AnsiString {
    #[pyo3(get, set)]
    pub vec: Vec<AnsiChar>,
}

// non-python methods
impl AnsiString {
    pub fn len(&self) -> usize {
        self.vec.len()
    }

    #[inline]
    pub fn new_fore(str: &str, fore: (u8, u8, u8)) -> AnsiString {
        AnsiString::new(str, Some(fore), None)
    }

    #[inline]
    pub fn new_back(str: &str, back: (u8, u8, u8)) -> AnsiString {
        AnsiString::new(str, None, Some(back))
    }

    #[inline]
    pub fn new_colorless(str: &str) -> AnsiString {
        AnsiString::new(str, None, None)
    }
}

// python methods
// TODO: add a function to render without formatting
// TODO: make object python subscriptable
#[pymethods]
impl AnsiString {
    #[new]
    #[pyo3(signature = (s, fore=None, back=None))]
    #[inline]
    pub fn new(s: &str, fore: Option<(u8, u8, u8)>, back: Option<(u8, u8, u8)>) -> Self {
        let mut vec: Vec<AnsiChar> = Vec::with_capacity(s.len());

        for c in s.chars() {
            vec.push(AnsiChar::new(c, fore, back));
        }

        Self { vec: vec }
    }

    // optimized to_string
    pub fn to_string(&self, mode: Option<ColorMode>) -> String {
        let colormode = &mode.unwrap_or(ColorMode::TRUECOLOR);

        if self.vec.len() == 0 {
            return String::new();
        }
        // the minimum size of the final result is the lenght of the string
        let mut result: String = String::with_capacity(self.len());

        // track cursor states
        let mut current_background_color: Option<AnsiColor> = None;
        let mut current_foreground_color: Option<AnsiColor> = None;
        let mut current_graphics_state: AnsiGraphics = AnsiGraphics::empty();

        for achar in &self.vec {
            let need_update = current_background_color != achar.back_color
                || current_foreground_color != achar.fore_color
                || current_graphics_state != achar.graphics;

            if need_update {
                if current_background_color.is_some() || current_foreground_color.is_some() || !current_graphics_state.is_empty() {
                    result += &ANSIRESET;
                }
                // set background color
                if let Some(c) = achar.back_color {
                    result += &c.to_string(colormode, &ColorGround::BACK);
                }

                // set foreground color
                if let Some(c) = achar.fore_color {
                    result += &c.to_string(colormode, &ColorGround::FORE);
                }

                // set graphics
                if !achar.graphics.is_empty() {
                    result += &achar.graphics.to_string(false);
                }

                current_background_color = achar.back_color;
                current_foreground_color = achar.fore_color;
                current_graphics_state = achar.graphics;
            }

            result.push(achar.char);
        }
        // append reset token and return
        result + "\x1b[0m"
    }

    pub fn split_at(&self, mid: usize) -> (AnsiString, AnsiString) {
        let vecs = self.vec.split_at(mid);
        (
            Self {
                vec: vecs.0.to_vec(),
            },
            Self {
                vec: vecs.1.to_vec(),
            },
        )
    }

    pub fn cut_at(&self, end: usize) -> AnsiString {
        let vecs = self.vec.split_at(end);
        Self {
            vec: vecs.0.to_vec(),
        }
    }

    pub fn add_graphics(&mut self, agm: AnsiGraphics) {
        for ac in &mut self.vec {
            ac.graphics = ac.graphics | agm;
        }
    }

    // python operation add
    pub fn __add__(&mut self, other: &Self) -> Self {
        let mut new_vec: Vec<AnsiChar> = Vec::with_capacity(self.vec.len() + other.vec.len());
        new_vec.append(&mut self.vec.clone());
        new_vec.append(&mut other.vec.clone());

        AnsiString { vec: new_vec }
    }

    // python len function
    pub fn __len__(&self) -> usize {
        self.len()
    }

    // python __str__ magic function
    pub fn __str__(&self) -> String {
        self.to_string(None)
    }

    // python __eq__ magic function
    pub fn __eq__(&self, other: &Self) -> bool {
        self == other
    }
}

impl Add for AnsiString {
    type Output = Self;

    fn add(self, other: Self) -> Self::Output {
        let mut new_vec: Vec<AnsiChar> = Vec::with_capacity(self.vec.len() + other.vec.len());
        new_vec.append(&mut self.vec.clone());
        new_vec.append(&mut other.vec.clone());

        AnsiString { vec: new_vec }
    }
}
