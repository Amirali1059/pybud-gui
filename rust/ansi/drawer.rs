use pyo3::prelude::*;

use crate::ansi::string::AnsiString;
use crate::ansi::ColorMode;

use super::AnsiColor;

#[derive(Clone, Copy)]
struct Size {
    height: usize,
    width: usize
}

#[derive(Clone)]
#[pyclass]
pub struct Drawer {
    size: Size,
    #[pyo3(get, set)]
    plane: Vec<AnsiString>,
}

fn get_string_with_len(len: usize) -> String {
    " ".repeat(len).to_string()
}

// non-python methods
impl Drawer {
    fn check_write_position(&self, pos: (usize, usize)) -> bool{
        //assert!(pos.0 <= self.size.height);
        //assert!(pos.1 <= self.size.width);
        (pos.0 >= self.size.height) || (pos.1 >= self.size.width)
    }
}

// python methods
#[pymethods]
impl Drawer {
    const DEFAULT_PLANE_COLOR: (u8, u8, u8) = (110, 90, 250);
    #[new]
    #[inline]
    pub fn new(size: (usize, usize), plane_color: Option<(u8, u8, u8)>) -> Drawer {
        let default_or_given_plane_color = match plane_color {
            None => {Self::DEFAULT_PLANE_COLOR}
            Some(c) => {c}
        };

        let mut plane: Vec<AnsiString> = Vec::with_capacity(size.0);
        for _ in 0..size.0 {
            plane.push(AnsiString::new_back(get_string_with_len(size.1).as_str(), default_or_given_plane_color));
        }
        
        Drawer {
            size: Size {
                height: size.0,
                width: size.1
            },
            plane: plane
        }
    }

    pub fn render(&self, mode: &ColorMode) -> String {
        assert!(self.plane.len() > 0);
        let mut _render = String::with_capacity(self.size.width * self.size.height);
        for p in &self.plane {
            _render.push_str((p.to_string(mode) + "\n").as_str())
        }
        _render
    }

    // python __str__ magic function
    pub fn __str__(&self) -> String{
        self.render(&ColorMode::TRUECOLOR)
    }

    pub fn place(&mut self, astr: &AnsiString, pos: (usize, usize), assign: bool) {
        if self.check_write_position(pos) {
            return
        }

        let write_len = astr.len();
        let end_idx = pos.1 + write_len;

        if end_idx > self.size.width {
            let mut _ansi_string = astr.clone();
            _ansi_string = _ansi_string.cut_at(write_len - (end_idx - self.size.width));
            self.plane[pos.0].place(&_ansi_string, pos.1, assign);
        } else {
            self.plane[pos.0].place(&astr, pos.1, assign);
        }
    }

    pub fn center_place(&mut self, astr: &AnsiString, ypos: usize, assign: bool) {
        let xpos: usize = (self.size.width - astr.len()) / 2;
        self.place(astr, (ypos, xpos), assign);
    }

    pub fn place_str(&mut self, _str: &str, pos: (usize, usize)) {
        // checks if we can write, and if index is out of bounds, returns
        if self.check_write_position(pos) {
            return
        }

        let write_len = _str.len();
        let end_idx = pos.1 + write_len;

        if end_idx > self.size.width {
            let _string = _str.split_at(write_len - (end_idx - self.size.width)).0;
            self.plane[pos.0].place_str(_string, pos.1);
        } else {
            self.plane[pos.0].place_str(_str, pos.1);
        }
    }

    pub fn center_place_str(&mut self, str: &str, ypos: usize) {
        let xpos: usize = (self.size.width - str.len()) / 2;
        self.place_str(str, (ypos, xpos));
    }

    pub fn place_drawer(&mut self, other: &Self, pos: (usize, usize), border: bool) {
        if self.check_write_position(pos) {
            return
        }

        for i in pos.0..self.size.height {
            // reletive height
            let rh: usize = i - pos.0;

            if rh > (other.size.height - 1) {
                break;
            }

            if border {
                // other.plane's reletive line
                let mut otprl = other.plane[rh].clone();

                for i in 0..other.size.width{
                    match otprl.vec[i].back_color {
                        None => {},
                        Some(bc) => {
                            otprl.vec[i].back_color = Some(AnsiColor {
                            0: (bc.0 as f32 * 0.9) as u8,
                            1: (bc.1 as f32 * 0.9) as u8,
                            2: (bc.2 as f32 * 0.9) as u8,
                            });}
                    }
                }

                self.plane[i].place(&otprl, pos.1, false);
                
            } else {
                self.plane[i].place(&other.plane[rh], pos.1, false);
            }
            
        }
    }
}