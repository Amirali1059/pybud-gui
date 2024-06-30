use pyo3::prelude::*;

use std::collections::HashMap;
use std::ops::Add;

use super::string::AnsiString;
use super::{AnsiColor, AnsiGraphics, ColorGround, ColorMode};

#[pyclass]
#[derive(Clone)]
pub struct AnsiChar {
    #[pyo3(get, set)]
    pub char: char,
    #[pyo3(get, set)]
    pub back_color: Option<AnsiColor>,
    #[pyo3(get, set)]
    pub fore_color: Option<AnsiColor>,
    #[pyo3(get, set)]
    pub graphics: AnsiGraphics,
}

#[pymethods]
impl AnsiChar {
    #[new]
    #[inline]
    pub fn new(char: char, fore: Option<(u8, u8, u8)>, back: Option<(u8, u8, u8)>) -> AnsiChar {
        Self {
            char: char,
            back_color: match back {
                Some(back) => Some(AnsiColor(back.0, back.1, back.2)),
                None => {None}
            },
            fore_color: match fore {
                Some(fore) => {Some(AnsiColor(fore.0, fore.1, fore.2))},
                None => {None}
            },
            graphics: AnsiGraphics::new(),
        }
    }

    pub fn to_string(&self, mode: &ColorMode) -> String {
        let mut pre = String::new();
        pre.push_str(self.graphics.to_string(false).as_str());
        match &self.back_color {
            Some(back) => {pre += back.to_string(mode, &ColorGround::BACK).as_str()},
            None => {}
        };
        match &self.fore_color {
            Some(fore) => {pre += fore.to_string(mode, &ColorGround::FORE).as_str()},
            None => {}
        };
        
        let mut post = String::new();
        post += self.graphics.to_string(false).as_str();

        format!("{}{}{}", pre, self.char, post)
    }

    // python __str__ magic function
    pub fn __str__(&self) -> String{
        self.to_string(&ColorMode::TRUECOLOR)
    }

    pub fn set(&mut self, c: char) {
        self.char = c;
    }

    pub fn as_ansistring(&self) -> AnsiString {
        AnsiString {
            vec: [self.clone()].to_vec()
        }
    }

    // python __add__ magic function
    pub fn __add__(&self, other: Self) -> AnsiString{
        self.clone().add(other)
    }
}

impl Add for AnsiChar {
    type Output = AnsiString;

    fn add(self, other: Self) -> Self::Output {
        AnsiString {
            vec: [self, other].to_vec(),
        }
    }
}