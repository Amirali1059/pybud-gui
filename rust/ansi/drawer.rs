use pyo3::prelude::*;

use crate::ansi;

use crate::ansi::string::AnsiString;
use crate::ansi::ColorMode;

use super::AnsiColor;

#[pyclass]
#[derive(Clone, Copy)]
struct Size {
    height: usize,
    width: usize
}

#[pyclass]
pub struct Drawer {
    size: Size,
    plane: Vec<AnsiString>,
}

fn get_string_with_len(len: usize) -> String {
    " ".repeat(len).to_string()
}

#[pymethods]
impl Drawer {
    #[new]
    #[inline]
    pub fn new(size: (usize, usize), plane_color: Option<(u8, u8, u8)>) -> Drawer {
        let mut plane: Vec<AnsiString> = Vec::with_capacity(size.0);
        for _ in 0..size.0 {
            plane.push(AnsiString::new_back(get_string_with_len(size.1).as_str(), plane_color));
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
        let mut _render = String::with_capacity(self.size.width * self.size.width);
        for p in self.plane.clone() {
            _render.push_str((p.to_string(mode) + "\n").as_str())
        }
        _render
    }

    // python __str__ magic function
    pub fn __str__(&self) -> String{
        self.render(&ColorMode::TrueColor)
    }

    fn check_write_position(&self, pos: (usize, usize)) -> bool{
        //assert!(pos.0 <= self.size.height);
        //assert!(pos.1 <= self.size.width);

        (pos.0 == self.size.height) || (pos.1 == self.size.width) ||
        (pos.0 > self.size.height) || (pos.1 > self.size.width)
    }

    pub fn place_str(&mut self, str: &str, pos: (usize, usize)) {
        // checks if we can write, and if index is out of bounds, returns
        if self.check_write_position(pos) {
            return
        }

        let mut _string = str.to_string();

        let write_len = str.len();
        let end_idx = pos.1 + write_len;

        if end_idx > self.size.width {
            _string = _string.split_at(write_len - (end_idx - self.size.width)).0.to_string();
        }

        self.plane[pos.0].place_str(_string.as_str(), pos.1);
    }

    pub fn place(&mut self, astr: &AnsiString, pos: (usize, usize), assign: bool) {
        if self.check_write_position(pos) {
            return
        }

        let mut _ansi_string = astr.clone();

        let write_len = _ansi_string.len();
        let end_idx = pos.1 + write_len;

        if end_idx > self.size.width {
            _ansi_string = _ansi_string.split_at(write_len - (end_idx - self.size.width)).0;
        }

        self.plane[pos.0].place(&_ansi_string, pos.1, assign);
    }

    pub fn center_place(&mut self, astr: &AnsiString, ypos: usize, assign: bool) {
        let xpos: usize = (self.size.width - astr.len()) / 2;
        self.place(astr, (ypos, xpos), assign);
    }

    pub fn center_place_str(&mut self, str: &str, ypos: usize) {
        let xpos: usize = (self.size.width - str.len()) / 2;
        self.place_str(str, (ypos, xpos));
    }

    pub fn place_drawer(&mut self, other: &Self, pos: (usize, usize), border: bool) {
        if self.check_write_position(pos) {
            return
        }

        for i in pos.0..self.plane.len() {
            // reletive pos.0
            let rp0 = i - pos.0;

            if rp0 > (other.plane.len() - 1) {
                break;
            }  
            if !border {
                self.plane[i].place(&other.plane[i - pos.0], pos.1, false);
            } else {
                // other.plane's reletive line
                let otprl = other.plane[i - pos.0].clone();
                // border + otprl
                let mut brl: AnsiString = otprl;
                // vector length
                let vl = brl.vec.len();

                for i in 0..vl{
                    match brl.vec[i].back_color {
                        None => {},
                        Some(bc) => {
                            brl.vec[i].back_color = Some(AnsiColor {
                            0: (bc.0 as f32 * 0.9) as u8,
                            1: (bc.1 as f32 * 0.9) as u8,
                            2: (bc.2 as f32 * 0.9) as u8,
                            });}
                    }
                }

                // if rp0 == 0{
                //     let bc0 = brl.vec[0].back_color.unwrap();
                //     brl.vec[0].back_color = Some(AnsiColor {
                //         0: (bc0.0 as f32 * 0.85) as u8,
                //         1: (bc0.1 as f32 * 0.85) as u8,
                //         2: (bc0.2 as f32 * 0.85) as u8,
                //     });

                //     for i in 1..(vl -1){
                //         let bc0 = brl.vec[i].back_color.unwrap();
                //         brl.vec[i].back_color = Some(AnsiColor {
                //             0: (bc0.0 as f32 * 0.9) as u8,
                //             1: (bc0.1 as f32 * 0.9) as u8,
                //             2: (bc0.2 as f32 * 0.9) as u8,
                //         });
                //     }

                //     let bc0 = brl.vec[(vl -1)].back_color.unwrap();
                //     brl.vec[(vl -1)].back_color = Some(AnsiColor {
                //         0: (bc0.0 as f32 * 0.80) as u8,
                //         1: (bc0.1 as f32 * 0.80) as u8,
                //         2: (bc0.2 as f32 * 0.80) as u8,
                //     });
                    
                // } else if rp0 == (other.plane.len() -1){
                //     let bc0 = brl.vec[0].back_color.unwrap();
                //     brl.vec[0].back_color = Some(AnsiColor {
                //         0: (bc0.0 as f32 * 0.65) as u8,
                //         1: (bc0.1 as f32 * 0.65) as u8,
                //         2: (bc0.2 as f32 * 0.65) as u8,
                //     });

                //     for i in 1..(vl - 1){
                //         let bc0 = brl.vec[i].back_color.unwrap();
                //         brl.vec[i].back_color = Some(AnsiColor {
                //             0: (bc0.0 as f32 * 0.6) as u8,
                //             1: (bc0.1 as f32 * 0.6) as u8,
                //             2: (bc0.2 as f32 * 0.6) as u8,
                //         });
                //     }

                //     let bc0 = brl.vec[(vl - 1)].back_color.unwrap();
                //     brl.vec[(vl - 1)].back_color = Some(AnsiColor {
                //         0: (bc0.0 as f32 * 0.55) as u8,
                //         1: (bc0.1 as f32 * 0.55) as u8,
                //         2: (bc0.2 as f32 * 0.55) as u8,
                //     });
                // } else {
                //     let bc0 = brl.vec[0].back_color.unwrap();
                //     brl.vec[0].back_color = Some(AnsiColor {
                //         0: (bc0.0 as f32 * 0.8) as u8,
                //         1: (bc0.1 as f32 * 0.8) as u8,
                //         2: (bc0.2 as f32 * 0.8) as u8,
                //     });

                //     let l = brl.vec.len();
                //     let bcl = brl.vec[l -1].back_color.unwrap();
                //     brl.vec[l -1].back_color = Some(AnsiColor {
                //         0: (bc0.0 as f32 * 0.7) as u8,
                //         1: (bc0.1 as f32 * 0.7) as u8,
                //         2: (bc0.2 as f32 * 0.7) as u8,
                //     });
                // }

                self.plane[i].place(&brl, pos.1, false);
                
            }
            
        }
    }
}