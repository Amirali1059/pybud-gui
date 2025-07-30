use pyo3::prelude::*;

use super::AnsiColor;
use crate::ansi::char::AnsiChar;
use crate::ansi::string::AnsiString;
use crate::ansi::{AnsiGraphics, ColorGround, ColorMode, ANSIRESET};

#[pyclass]
#[derive(Clone)]
pub struct Plane {
    width: usize,
    height: usize,
    content: Vec<Vec<AnsiChar>>,
}

impl Plane {
    #[inline]
    fn assert_write_position(&self, posx: usize, posy: usize) -> bool {
        posy < self.height && posx < self.width
    }

    #[inline(always)]
    pub fn set_char(&mut self, c: char, posx: usize, posy: usize) {
        if !self.assert_write_position(posx, posy) {
            return;
        }
        // Use unsafe to avoid double bounds checking
        unsafe {
            self.content
                .get_unchecked_mut(posy)
                .get_unchecked_mut(posx)
                .char = c;
        }
    }

    #[inline(always)]
    pub fn assign(&mut self, achar: &AnsiChar, posx: usize, posy: usize) {
        if !self.assert_write_position(posx, posy) {
            return;
        }
        // Use unsafe to avoid double bounds checking
        unsafe {
            let cell = self.content.get_unchecked_mut(posy).get_unchecked_mut(posx);
            cell.char = achar.char;
            cell.fore_color = achar.fore_color;
            if achar.back_color.is_some() {
                cell.back_color = achar.back_color;
            }
            cell.graphics = achar.graphics;
        }
    }
}

// python methods
#[pymethods]
impl Plane {
    #[new]
    #[pyo3(signature = (width, height, color=None))]
    #[inline]
    pub fn new(width: usize, height: usize, color: Option<AnsiColor>) -> Plane {
        let achar = AnsiChar::new_colored(' ', None, color);
        Plane {
            width: width,
            height: height,
            content: vec![vec![achar; width]; height],
        }
    }
}

#[derive(Clone)]
#[pyclass]
pub struct DrawerFast {
    plane: Plane,
}

// python methods
#[pymethods]
impl DrawerFast {
    #[new]
    #[pyo3(signature = (width, height, plane_color=None))]
    #[inline]
    pub fn new(width: usize, height: usize, plane_color: Option<AnsiColor>) -> DrawerFast {
        DrawerFast {
            plane: Plane::new(width, height, plane_color),
        }
    }

    #[pyo3(signature = (color=None))]
    pub fn fill(&mut self, color: Option<AnsiColor>) {
        let achar = AnsiChar::new_colored(' ', None, color);
        self.plane.content = vec![vec![achar; self.plane.width]; self.plane.height];
    }

    #[getter]
    pub fn height(&self) -> usize {
        self.plane.height
    }

    #[getter]
    pub fn width(&self) -> usize {
        self.plane.width
    }

    pub fn render(&self, mode: Option<ColorMode>) -> String {
        let colormode = &mode.unwrap_or(ColorMode::TRUECOLOR);

        // the minimum size of the final result is width * height
        let mut result: String = String::with_capacity(self.plane.width * self.plane.height * 4);

        for i in 0..self.plane.height {
            // Track cursor states for each line
            let mut current_background_color: Option<AnsiColor> = None;
            let mut current_foreground_color: Option<AnsiColor> = None;
            let mut current_graphics_state: AnsiGraphics = AnsiGraphics::empty();

            unsafe {
                for achar in self.plane.content.get_unchecked(i) {
                    let need_update = current_background_color != achar.back_color
                        || current_foreground_color != achar.fore_color
                        || current_graphics_state != achar.graphics;

                    if need_update {
                        if current_background_color.is_some()
                            || current_foreground_color.is_some()
                            || !current_graphics_state.is_empty()
                        {
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
                result.push_str(ANSIRESET);
            }
            if i != (self.plane.height - 1) {
                result.push('\n');
            }
        }

        result
    }

    #[pyo3(signature = (text, posx, posy, fore_color=None, back_color=None))]
    pub fn text(
        &mut self,
        text: &str,
        posx: usize,
        posy: usize,
        fore_color: Option<AnsiColor>,
        back_color: Option<AnsiColor>,
    ) {
        let mut chars = text.chars();
        for i in 0..text.len() {
            match chars.next() {
                Some(c) => {
                    if !self.plane.assert_write_position(posx + i, posy) {
                        continue;
                    }
                    unsafe {
                        let cell = self
                            .plane.content
                            .get_unchecked_mut(posy)
                            .get_unchecked_mut(posx + i);
                        cell.char = c;
                        if fore_color.is_some() {
                            cell.fore_color = fore_color.or(cell.fore_color);
                        }
                        if back_color.is_some() {
                            cell.back_color = back_color.or(cell.back_color);
                        }
                    }
                }
                None => {
                    break;
                }
            }
        }
    }

    pub fn text_colored(&mut self, text: &AnsiString, posx: usize, posy: usize) {
        for i in 0..text.len() {
            match text.vec.get(i) {
                Some(c) => {
                    self.plane.assign(c, posx + i, posy);
                }
                None => {
                    break;
                }
            }
        }
    }

    #[pyo3(signature = (text, posy, fore_color=None, back_color=None))]
    pub fn text_centered(
        &mut self,
        text: &str,
        posy: usize,
        fore_color: Option<AnsiColor>,
        back_color: Option<AnsiColor>,
    ) {
        let width = self.plane.width;
        let lenght = text.len();
        let posx = if width > lenght {
            (width - lenght) / 2
        } else {
            0
        };

        self.text(text, posx, posy, fore_color, back_color)
    }

    pub fn text_colored_centered(&mut self, text: &AnsiString, posy: usize) {
        let width = self.plane.width;
        let lenght = text.len();
        let posx = if width > lenght {
            (width - lenght) / 2
        } else {
            0
        };

        self.text_colored(text, posx, posy)
    }

    #[pyo3(signature = (posx, posy, width, height, border_color, fill_color=None))]
    pub fn rect(
        &mut self,
        posx: usize,
        posy: usize,
        width: usize,
        height: usize,
        border_color: AnsiColor,
        fill_color: Option<AnsiColor>,
    ) {
        for i in 0..height {
            for j in 0..width {
                let is_border = j == 0 || i == 0 || j == (width - 1) || i == (height - 1);
                self.plane.assign(
                    &AnsiChar::new_colored(
                        ' ',
                        None,
                        if is_border {
                            Some(border_color)
                        } else {
                            fill_color.or(Some(border_color))
                        },
                    ),
                    posx + j,
                    posy + i,
                );
            }
        }
    }

    pub fn get_plane(&self) -> Plane {
        self.plane.clone()
    }

    pub fn place_drawer(&mut self, drawer: &DrawerFast, posx: usize, posy: usize) {
        for i in 0..drawer.plane.height {
            for j in 0..drawer.plane.width {
                self.plane.assign(&drawer.plane.content[i][j], posx + j, posy + i);
            }
        }
    }

    pub fn place_plane(&mut self, plane: &Plane, posx: usize, posy: usize) {
        for i in 0..plane.height {
            for j in 0..plane.width {
                self.plane.assign(&plane.content[i][j], posx + j, posy + i);
            }
        }
    }
}
