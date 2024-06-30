#![allow(unused)]
use ansi::char::AnsiChar;
use pyo3::prelude::*;

mod ansi;
use ansi::{AnsiColor, AnsiGraphicMode, AnsiGraphics, ColorGround, ColorMode};
use ansi::drawer::Drawer;
use ansi::string::AnsiString;

fn main(){
    
    let mut drawer_main = Drawer::new((11, 62), Some((110, 90, 250)));

    let mut drawer = Drawer::new((9, 60), Some((90, 180, 220)));
    
    let mut astr_title = AnsiString::new_fore( "Rust Drawer", Some((0, 255, 0)));
    astr_title.add_graphics(AnsiGraphicMode::Italic);
    astr_title.add_graphics(AnsiGraphicMode::Underline);
    
    let mut astr_title_bracets = AnsiString::new_fore("[             ]", Some((255, 0, 0)));
    astr_title_bracets.center_place(&astr_title, false);

    // place the text on the display
    drawer.center_place(&astr_title_bracets, 4, false);

    // print the drawer
    print!("{}", drawer.render(&ColorMode::TrueColor));


    drawer_main.place_drawer(&drawer, (1, 1), true);

    // print the drawer
    print!("{}", drawer_main.render(&ColorMode::TrueColor));
    
}