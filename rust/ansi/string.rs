use pyo3::prelude::*;

use std::ops::Add;
use std::str::FromStr;

use crate::ansi::AnsiGraphics; // TODO: implement optimized rendering

use super::{AnsiGraphicMode, ColorGround, ColorMode, ANSIRESET, RESET_BACKGROUND, RESET_FOREGROUND};
use super::char::AnsiChar;

#[pyclass]
#[derive(Clone)]
pub struct AnsiString {
    #[pyo3(get, set)]
    pub vec: Vec<AnsiChar>,
}

fn min(a: usize, b: usize) -> usize {
    if a > b {b} else {a}
}

fn max(a: usize, b: usize) -> usize {
    if a > b {a} else {b}
}

#[pymethods]
impl AnsiString {
    pub fn len(&self) -> usize {
        self.vec.len()
    }

    // python len function
    pub fn __len__(&self) -> usize {
        self.len()
    }
    // not optimized to_string, each character is rendered individually
    pub fn to_string_noopt(&self, mode: &ColorMode) -> String {
        let mut _string = String::new();
        for ac in &self.vec.clone() {
            _string.push_str(ac.to_string(mode).as_str());
            _string.push_str(ANSIRESET);
        }
        _string
    }

    // optimized to_string
    pub fn to_string(&self, mode: &ColorMode) -> String {
        // add the first character unoptimized
        let mut _string = self.vec[0].to_string(mode);

        for i in 1..self.vec.len() {
            // current AnsiChar
            let cac = &self.vec[i];
            // current fore color
            let cfc = &cac.fore_color;
            // current back color
            let cbc = &cac.back_color;
            // current AnsiGraphics
            let cag = &cac.graphics;

            // previus AnsiChar
            let pac = &self.vec[i-1];
            // previus fore color
            let pfc = &pac.fore_color;
            // previus back color
            let pbc = &pac.back_color;
            // previus AnsiGraphics
            let pag = &pac.graphics;

            // if color is changed, apply changes
            if (pbc != cbc) || (pfc != cfc) {
                // reset background
                _string.push_str(RESET_BACKGROUND);
                // reset foreground
                _string.push_str(RESET_FOREGROUND);
                
                // set background if exists
                _string.push_str(match cbc {
                    None => {String::new()},
                    Some(c) => {c.to_string(mode, &ColorGround::Back)},
                }.as_str());

                // set foreground if exists
                _string.push_str(match cfc {
                    None => {String::new()},
                    Some(c) => {c.to_string(mode, &ColorGround::Fore)},
                }.as_str());

                // write current AnsiGraphics AGAIN
                _string.push_str(cag.to_string(false).as_str());
            }

            if !pag.is_eq(&cag) {
                // reset previus AnsiGraphics
                _string.push_str(pag.to_string(true).as_str());
                // write current AnsiGraphics
                _string.push_str(cag.to_string(false).as_str());

            }
            
            _string.push(cac.char);
        }
        // append reset token and return
        _string + "\x1b[0m"
    }

    // python __str__ magic function
    pub fn __str__(&self) -> String{
        self.to_string(&ColorMode::TrueColor)
    }

    pub fn split_at(&self, mid: usize) -> (AnsiString, AnsiString){
        let vecs = self.vec.split_at(mid);
        (
            Self {vec: vecs.0.to_vec()},
            Self {vec: vecs.1.to_vec()}
        )
    }

    // main function for writing text
    pub fn place(&mut self, text: &AnsiString, pos: usize, assign: bool) {
        assert!(pos < self.len());

        let si = pos;
        let ei = min(pos + text.len(), self.vec.len());

        for i in si..ei {
            let ac = &text.vec[i - si];
            if assign {
                self.vec[i] = ac.clone();
            } else {
                self.vec[i] = AnsiChar {
                    char: ac.char,
                    fore_color: ac.fore_color,
                    back_color: if ac.back_color == None {self.vec[i].back_color} else {ac.back_color},
                    graphics: ac.graphics.clone(),
                }
            }
        }
    }

    pub fn place_str(&mut self, str: &str, pos: usize) {
        // TODO: negative positon values
        assert!(pos < self.len());

        let astr = AnsiString::new_colorless(str);
        self.place(&astr, pos, false);
        
    }

    pub fn center_place(&mut self, astr: &AnsiString, assign: bool) {
        assert!(self.len() > astr.len());

        let pos: usize = (self.len() - astr.len()) / 2;

        self.place(astr, pos, assign);
    }

    pub fn center_place_str(&mut self, str: &str) {
        assert!(self.len() > str.len());

        let pos: usize = (self.len() - str.len()) / 2;

        let astr = AnsiString::new_colorless(str);
        self.place(&astr, pos, false);
    }

    pub fn add_graphics(&mut self, agm: AnsiGraphicMode) {
        for ac in &mut self.vec {
            ac.graphics.add(agm);
        }
    }

    // python operation add
    pub fn __add__(&mut self, other: &Self) -> Self{
        let mut r = self.clone();
        r.vec.append(&mut other.vec.clone());

        r
    }

    #[new]
    #[inline]
    pub fn new(str: &str, fore: Option<(u8, u8, u8)>, back: Option<(u8, u8, u8)>) -> AnsiString {
        let mut vec: Vec<AnsiChar> = Vec::with_capacity(str.len());
    
        for c in str.chars() {
            vec.push(AnsiChar::new(c, fore, back));
        }

        AnsiString {vec: vec}
    }

    #[staticmethod]
    #[inline]
    pub fn new_fore(str: &str, fore: Option<(u8, u8, u8)>) -> AnsiString {
        AnsiString::new(str, fore, None)
    }

    #[staticmethod]
    #[inline]
    pub fn new_back(str: &str, back: Option<(u8, u8, u8)>) -> AnsiString {
        AnsiString::new(str, None, back)
    }

    #[staticmethod]
    #[inline]
    pub fn new_colorless(str: &str) -> AnsiString {
        AnsiString::new(str, None, None)
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